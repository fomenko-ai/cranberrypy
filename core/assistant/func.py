import os
import json
import fnmatch
from pathlib import Path
from typing import List, Literal, Optional, Union


def download_hf_model(
        repo_id: str,
        filename: str,
        local_dir: Optional[Union[str, os.PathLike[str]]] = None,
        local_dir_use_symlinks: Union[bool, Literal["auto"]] = "auto",
        cache_dir: Optional[Union[str, os.PathLike[str]]] = None) -> str:

    try:
        from huggingface_hub import HfFileSystem, hf_hub_download
        from huggingface_hub.utils import validate_repo_id
    except ImportError as exc:
        raise ImportError(
            "Llama.from_pretrained requires the huggingface-hub package. "
            "You can install it with `pip install huggingface-hub`."
        ) from exc

    validate_repo_id(repo_id)

    hffs = HfFileSystem()

    files = [
        file["name"] if isinstance(file, dict) else file
        for file in hffs.ls(repo_id)
    ]

    # split each file into repo_id, subfolder, filename
    file_list: List[str] = []
    for file in files:
        rel_path = Path(file).relative_to(repo_id)
        file_list.append(str(rel_path))

    matching_files = [
        file for file in file_list if fnmatch.fnmatch(file, filename)
    ]  # type: ignore

    if len(matching_files) == 0:
        raise ValueError(
            f"No file found in {repo_id} that match {filename}\n\n"
            f"Available Files:\n{json.dumps(file_list)}"
        )

    if len(matching_files) > 1:
        raise ValueError(
            f"Multiple files found in {repo_id} matching {filename}\n\n"
            f"Available Files:\n{json.dumps(files)}"
        )

    (matching_file,) = matching_files

    subfolder = str(Path(matching_file).parent)
    filename = Path(matching_file).name

    # download the file
    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        subfolder=subfolder,
        local_dir=local_dir,
        local_dir_use_symlinks=local_dir_use_symlinks,
        cache_dir=cache_dir,
    )

    if local_dir is None:
        model_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            subfolder=subfolder,
            local_dir=local_dir,
            local_dir_use_symlinks=local_dir_use_symlinks,
            cache_dir=cache_dir,
            local_files_only=True,
        )
    else:
        model_path = os.path.join(local_dir, filename)

    return model_path
