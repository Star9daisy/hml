import awkward as ak
import numba as nb
import vector

from ..types import AwkwardArray, AwkwardArrayBuilder, ROOTEvents

vector.register_awkward()


def get_branch(
    events: ROOTEvents, branch: str, as_momentum: bool = False
) -> AwkwardArray:
    if events[branch].top_level:
        return get_top_branch(events, branch, as_momentum)
    else:
        return get_sub_branch(events, branch, as_momentum)


def get_top_branch(
    events: ROOTEvents, branch: str, as_momentum: bool = False
) -> AwkwardArray:
    if not events[branch].top_level:
        raise ValueError(f"{branch} is not a top-level branch")

    # Pt
    if f"{branch}.PT" in events:
        pt = events[f"{branch}.PT"].array()
    elif f"{branch}.ET" in events:
        pt = events[f"{branch}.ET"].array()
    elif f"{branch}.MET" in events:
        pt = events[f"{branch}.MET"].array()
    else:
        raise ValueError(f"No PT/ET/MET branch found for {branch}")

    # Eta
    eta = events[f"{branch}.Eta"].array()

    # Phi
    phi = events[f"{branch}.Phi"].array()

    # Mass
    if f"{branch}.Mass" in events:
        mass = events[f"{branch}.Mass"].array()
    else:
        mass = ak.zeros_like(pt)

    return ak.zip(
        {"pt": pt, "eta": eta, "phi": phi, "mass": mass},
        with_name="Momentum4D" if as_momentum else None,
    )


def get_sub_branch(
    events: ROOTEvents, branch: str, as_momentum: bool = False
) -> AwkwardArray:
    if events[branch].top_level:
        raise ValueError(f"{branch} is not a sub-branch")

    if ".Constituents" not in branch:
        raise ValueError(f"{branch} is not supported yet")

    constituents = events[branch].array()

    reference_ids = constituents["refs"]

    tracks = get_top_branch(events, "EFlowTrack")
    track_ids = events["EFlowTrack.fUniqueID"].array()

    photons = get_top_branch(events, "EFlowPhoton")
    photon_ids = events["EFlowPhoton.fUniqueID"].array()

    hadrons = get_top_branch(events, "EFlowNeutralHadron")
    hadron_ids = events["EFlowNeutralHadron.fUniqueID"].array()

    eflows = ak.concatenate([tracks, photons, hadrons], axis=1)
    eflow_ids = ak.concatenate([track_ids, photon_ids, hadron_ids], axis=1)
    eflows["id"] = eflow_ids

    builder = ak.ArrayBuilder()
    builder = builder_from_eflows(reference_ids, eflows, builder, as_momentum)

    return builder.snapshot()


@nb.njit
def builder_from_eflows(
    reference_ids: AwkwardArray,
    eflows: AwkwardArray,
    builder: AwkwardArrayBuilder,
    as_momentum: bool = False,
) -> AwkwardArrayBuilder:  # pragma: no cover
    for ref_ids_per_event, eflows_per_event in zip(reference_ids, eflows):
        builder.begin_list()

        for ref_ids_per_jet in ref_ids_per_event:
            builder.begin_list()

            for ref_id in ref_ids_per_jet:
                for eflow in eflows_per_event:
                    if eflow.id == ref_id:
                        if as_momentum:
                            builder.begin_record("Momentum4D")
                        else:
                            builder.begin_record()

                        builder.field("pt").append(eflow.pt)
                        builder.field("eta").append(eflow.eta)
                        builder.field("phi").append(eflow.phi)
                        builder.field("mass").append(eflow.mass)
                        builder.end_record()
                        break

            builder.end_list()

        builder.end_list()

    return builder
