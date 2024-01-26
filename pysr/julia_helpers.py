"""Functions for initializing the Julia environment and installing deps."""
import os
import warnings

# Required to avoid segfaults (https://juliapy.github.io/PythonCall.jl/dev/faq/)
if os.environ["PYTHON_JULIACALL_HANDLE_SIGNALS"] not in {"yes", ""}:
    warnings.warn(
        "PYTHON_JULIACALL_HANDLE_SIGNALS environment variable is set to something other than 'yes' or ''. "
        + "You will experience segfaults if running with multithreading."
    )

os.environ["PYTHON_JULIACALL_HANDLE_SIGNALS"] = "yes"

import juliacall
import juliapkg

jl = juliacall.newmodule("PySR")

from juliacall import convert as jl_convert

jl.seval("using PythonCall: PythonCall")
PythonCall = jl.PythonCall

juliainfo = None
julia_initialized = False
julia_kwargs_at_initialization = None
julia_activated_env = None


def _get_io_arg(quiet):
    io = "devnull" if quiet else "stderr"
    return f"io={io}"


def _escape_filename(filename):
    """Turn a path into a string with correctly escaped backslashes."""
    str_repr = str(filename)
    str_repr = str_repr.replace("\\", "\\\\")
    return str_repr


def _backend_version_assertion():
    backend_version = jl.seval("string(SymbolicRegression.PACKAGE_VERSION)")
    expected_backend_version = juliapkg.status(target="SymbolicRegression").version
    if backend_version != expected_backend_version:  # pragma: no cover
        warnings.warn(
            f"PySR backend (SymbolicRegression.jl) version {backend_version} "
            f"does not match expected version {expected_backend_version}. "
            "Things may break. "
        )


def _load_cluster_manager(cluster_manager):
    jl.seval(f"using ClusterManagers: addprocs_{cluster_manager}")
    return jl.seval(f"addprocs_{cluster_manager}")
