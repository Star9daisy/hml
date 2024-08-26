import awkward as ak
import numba as nb
import uproot
import vector

vector.register_awkward()


def branch_to_momentum4d(branch: uproot.TBranch):
    """Convert a branch read by uproot to a Momentum4D record array.

    Top-level branches supported by default are (except ScalarHT):

        - Particle -> GenParticle
        - Track -> Track
        - Tower -> Tower
        - EFlowTrack -> Track
        - EFlowPhoton -> Tower
        - EFlowNeutralHadron -> Tower
        - GenJet -> Jet
        - GenMissingET -> MissingET
        - Jet -> Jet
        - Electron -> Electron
        - Photon -> Photon
        - Muon -> Muon
        - FatJet -> Jet
        - MissingET -> MissingET

    Other custom branches could be converted correctly if they are output by
    Delphes and of the class as above.

    Parameters
    ----------
    branch : uproot.TBranch
        The branch to convert.

    Returns
    -------
    ak.Array
        The converted branch as a Momentum4D record array.

    Examples
    --------
    >>> import uproot
    >>> from hml.operations import uproot_ops as upo

    >>> events = uproot.open("tag_1_delphes_events.root")["Delphes"]
    >>> branch = events["Jet"]
    >>> momentum4d = upo.branch_to_momentum4d(branch)
    >>> momentum4d.typestr
    '100 * var * Momentum4D[pt: float32, eta: float32, phi: float32, mass: float32]'

    >>> branch = events["Jet.Constituents"]
    >>> momentum4d = upo.branch_to_momentum4d(branch)
    >>> momentum4d.typestr
    '100 * var * var * Momentum4D[pt: float32, eta: float32, phi: float32, mass: float32]'

    """
    if branch.top_level:
        return top_level_branch_to_momentum4d(branch)
    else:
        return sub_level_branch_to_momentum4d(branch)


def top_level_branch_to_momentum4d(branch: uproot.TBranch) -> ak.Array:
    """Convert a top-level branch to a Momentum4D record array.

    Parameters
    ----------
    branch : uproot.TBranch
        The branch to convert.

    Returns
    -------
    ak.Array
        The converted branch as a Momentum4D record array.

    Raises
    ------
    ValueError
        If the branch does not have the required leaves (PT/ET/MET, Eta, Phi,
        Mass).

    Examples
    --------
    >>> import uproot
    >>> from hml.operations import uproot_ops as upo

    >>> events = uproot.open("tag_1_delphes_events.root")["Delphes"]
    >>> branch = events["Jet"]
    >>> momentum4d = upo.branch_to_momentum4d(branch)
    >>> momentum4d.typestr
    '100 * var * Momentum4D[pt: float32, eta: float32, phi: float32, mass: float32]'
    """
    if not branch.top_level:
        raise ValueError(f"{branch.name} is not a top-level branch.")

    # Pt
    if f"{branch.name}.PT" in branch.keys():
        pt = branch[f"{branch.name}.PT"].array()
    elif f"{branch.name}.ET" in branch.keys():
        pt = branch[f"{branch.name}.ET"].array()
    elif f"{branch.name}.MET" in branch.keys():
        pt = branch[f"{branch.name}.MET"].array()
    else:
        raise ValueError(
            f"branch {branch.name} does not have any of "
            f"{branch.name}.PT, {branch.name}.ET, {branch.name}.MET."
        )

    # Eta
    # if f"{branch.name}.Eta" in branch.keys():
    eta = branch[f"{branch.name}.Eta"].array()
    # else:
    # raise ValueError(f"branch {branch.name} does not have {branch.name}.Eta.")

    # Phi
    # if f"{branch.name}.Phi" in branch.keys():
    phi = branch[f"{branch.name}.Phi"].array()
    # else:
    # raise ValueError(f"branch {branch.name} does not have {branch.name}.Phi.")

    # Mass
    if f"{branch.name}.Mass" in branch.keys():
        mass = branch[f"{branch.name}.Mass"].array()
    else:
        mass = ak.zeros_like(pt)

    # Momentum4D
    momentum4d = ak.zip(
        {"pt": pt, "eta": eta, "phi": phi, "mass": mass}, with_name="Momentum4D"
    )

    return momentum4d


def sub_level_branch_to_momentum4d(branch: uproot.TBranch) -> ak.Array:
    """Convert a sub-level branch representing a physics object from events to a
    Momentum4D record array.

    Parameters
    ----------
    branch : uproot.TBranch
        The branch to convert.

    Returns
    -------
    ak.Array
        The converted branch as a Momentum4D record array.

    Examples
    --------
    >>> import uproot
    >>> from hml.operations import uproot_ops as upo

    >>> events = uproot.open("tag_1_delphes_events.root")["Delphes"]
    >>> branch = events["Jet.Constituents"]
    >>> momentum4d = upo.sub_level_branch_to_momentum4d(branch)
    >>> momentum4d.typestr
    '100 * var * var * Momentum4D[pt: float32, eta: float32, phi: float32, mass: float32]'
    """
    if branch.top_level:
        raise ValueError(f"{branch.name} is a top-level branch.")

    if ".Constituents" in branch.name:
        return constituents_to_momentum4d(branch)

    else:
        raise ValueError(f"{branch.name} is not supported yet.")


def constituents_to_momentum4d(constituents: uproot.TBranch) -> ak.Array:
    """Convert the constituents branch to a Momentum4D record array.

    Parameters
    ----------
    constituents : uproot.TBranch
        The constituents branch.

    Returns
    -------
    ak.Array
        The constituents as a Momentum4D record array.

    Examples
    --------
    >>> import uproot
    >>> from hml.operations import uproot_ops as upo

    >>> events = uproot.open("tag_1_delphes_events.root")["Delphes"]
    >>> momentum4d = upo.constituents_to_momentum4d(events["Jet.Constituents"])
    >>> momentum4d.typestr
    '100 * var * var * Momentum4D[pt: float32, eta: float32, phi: float32, mass: float32]'
    """
    reference_ids = constituents.array()["refs"]
    events = constituents.parent.parent

    tracks = top_level_branch_to_momentum4d(events["EFlowTrack"])
    track_ids = events["EFlowTrack.fUniqueID"].array()

    photons = top_level_branch_to_momentum4d(events["EFlowPhoton"])
    photon_ids = events["EFlowPhoton.fUniqueID"].array()

    hadrons = top_level_branch_to_momentum4d(events["EFlowNeutralHadron"])
    hadron_ids = events["EFlowNeutralHadron.fUniqueID"].array()

    eflows = ak.concatenate([tracks, photons, hadrons], axis=1)
    eflow_ids = ak.concatenate([track_ids, photon_ids, hadron_ids], axis=1)

    builder = retrieve_constituents_from_eflows(
        reference_ids, eflow_ids, eflows, ak.ArrayBuilder()
    )

    momentum4d = builder.snapshot()
    momentum4d = ak.values_astype(momentum4d, "float32")
    return momentum4d


@nb.njit
def retrieve_constituents_from_eflows(
    reference_ids: ak.Array,
    eflow_ids: ak.Array,
    eflows: ak.Array,
    builder: ak.ArrayBuilder,
) -> ak.ArrayBuilder:
    """Retrieve the constituents from the eflow branches based on the reference.

    Parameters
    ----------
    reference_ids : ak.Array
        The reference fUniqueIDs of the constituents.
    eflow_ids : ak.Array
        The eflow fUniqueIDs.
    eflows : ak.Array
        The eflow branch (from EFlowTrack, EFlowPhoton, EFlowNeutralHadron).
    builder : ak.ArrayBuilder
        The array builder to store the constituent data.

    Returns
    -------
    ak.ArrayBuilder
        The array builder with the constituents data.
    """
    for ref_ids_per_event, eflows_per_event, eflow_ids_per_event in zip(
        reference_ids, eflows, eflow_ids
    ):
        builder.begin_list()
        for ref_ids_per_jet in ref_ids_per_event:
            builder.begin_list()
            for ref_id in ref_ids_per_jet:
                for eflow, eflow_id in zip(eflows_per_event, eflow_ids_per_event):
                    if eflow_id == ref_id:
                        builder.begin_record("Momentum4D")
                        builder.field("pt").append(eflow.pt)
                        builder.field("eta").append(eflow.eta)
                        builder.field("phi").append(eflow.phi)
                        builder.field("mass").append(eflow.mass)
                        builder.end_record()
                        break
            builder.end_list()
        builder.end_list()

    return builder
