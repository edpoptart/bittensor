from bittensor.subtensor import subtensor
import types
from .record_replay import NeuroTrace


def decorate_class_methods(cls, method_names):
    for name in method_names:
        if hasattr(cls, name) and isinstance(getattr(cls, name), types.FunctionType):
            original_method = getattr(cls, name)
            decorated_method = NeuroTrace(original_method)
            setattr(cls, name, decorated_method)


methods_to_decorate = [
    "get_all_subnets_info",
    "get_subnet_info",
    "get_delegate_by_hotkey",
    "get_delegates",
    "get_delegated",
    "neuron_for_uid",
    "_do_delegation",
    "_do_undelegation",
    "_do_nominate",
    "get_balance",
    "get_current_block",
    "get_balances",
    "_do_set_weights",
    "_do_pow_register",
    "_do_burned_register",
    "_do_swap_hotkey",
    "_do_transfer",
    "_do_serve_axon",
    "_do_serve_prometheus",
    "_do_associate_ips",
    "_do_stake",
    "_do_unstake",
    "_do_root_register",
    "query_identity",
    "update_identity",
    "query_subtensor",
    "query_map_subtensor",
    "query_constant",
    "query_module",
    "state_call",
]

decorate_class_methods(subtensor, methods_to_decorate)
