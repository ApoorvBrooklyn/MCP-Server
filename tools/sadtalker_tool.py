"""
Deprecated: SadTalker integration retained only for reference. Not used in current pipeline.
"""

import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional


def _ensure_models_downloaded(sadtalker_dir: Path) -> None:
    """Ensure SadTalker checkpoints and GFPGAN assets exist; download if missing."""
    checkpoints_dir = sadtalker_dir / "checkpoints"
    gfpgan_dir = sadtalker_dir / "gfpgan" / "weights"
    need_download = not checkpoints_dir.exists() or not any(checkpoints_dir.iterdir())
    need_gfpgan = not gfpgan_dir.exists() or not any(gfpgan_dir.parent.iterdir())

    if need_download or need_gfpgan:
        script_path = sadtalker_dir / "scripts" / "download_models.sh"
        if script_path.exists():
            result = subprocess.run(["bash", str(script_path)], cwd=sadtalker_dir, capture_output=True, text=True)
            if result.returncode == 0:
                return
            # Fallback if wget missing
            if "wget: command not found" not in (result.stderr or "") + (result.stdout or ""):
                raise RuntimeError(f"Failed to download SadTalker models: {result.stderr or result.stdout}")
        # Python fallback downloader using requests
        _python_fallback_downloads(sadtalker_dir)


def _python_fallback_downloads(sadtalker_dir: Path) -> None:
    try:
        import requests
    except Exception as e:
        raise RuntimeError("requests not available to download models; install it or install wget") from e

    checkpoints_dir = sadtalker_dir / "checkpoints"
    gfpgan_weights_dir = sadtalker_dir / "gfpgan" / "weights"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)
    gfpgan_weights_dir.mkdir(parents=True, exist_ok=True)

    files = [
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar", checkpoints_dir / "mapping_00109-model.pth.tar"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar", checkpoints_dir / "mapping_00229-model.pth.tar"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors", checkpoints_dir / "SadTalker_V0.0.2_256.safetensors"),
        ("https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors", checkpoints_dir / "SadTalker_V0.0.2_512.safetensors"),
        ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth", gfpgan_weights_dir / "alignment_WFLW_4HG.pth"),
        ("https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth", gfpgan_weights_dir / "detection_Resnet50_Final.pth"),
        ("https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth", gfpgan_weights_dir / "GFPGANv1.4.pth"),
        ("https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth", gfpgan_weights_dir / "parsing_parsenet.pth"),
    ]

    def download(url: str, dest: Path) -> None:
        if dest.exists() and dest.stat().st_size > 0:
            return
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            tmp = dest.with_suffix(dest.suffix + ".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            tmp.replace(dest)

    for url, dest in files:
        download(url, dest)


def _ensure_python_dependencies(sadtalker_dir: Path) -> None:
    """Ensure required Python deps for SadTalker are installed in the active environment."""
    try:
        import skimage  # noqa: F401
    except Exception:
        # Install requirements
        req_files = [
            sadtalker_dir / "requirements.txt",
            sadtalker_dir / "requirements3d.txt",
            sadtalker_dir / "req.txt",
        ]
        python_exec = _get_python_exec()
        for req in req_files:
            if req.exists():
                subprocess.run([python_exec, "-m", "pip", "install", "-r", str(req)], check=False)
        # Ensure core missing packages
        subprocess.run([python_exec, "-m", "pip", "install", "scikit-image", "imageio", "imageio-ffmpeg"], check=False)


def _get_python_exec() -> str:
    """Use current Python interpreter to run SadTalker. Venv is optional."""
    return os.environ.get("PYTHON_EXECUTABLE", Path(os.sys.executable).as_posix())


def run_sadtalker(
    narration_wav: str,
    avatar_image: str,
    results_dir: str,
    *,
    enhancer: Optional[str] = "gfpgan",
    preprocess: str = "full",
    size: int = 512,
    still: bool = True,
    cpu: Optional[bool] = None,
) -> str:
    """Invoke SadTalker inference and return the generated mp4 path.

    Defaults prioritize quality: full-body preprocess, 512px, still mode, and GFPGAN enhancer.
    """
    sadtalker_dir = Path(__file__).resolve().parent.parent / "SadTalker"
    if not sadtalker_dir.exists():
        raise RuntimeError("SadTalker directory not found. Expected at viral-moment-pipeline/SadTalker")

    # Prepare models if not present
    _ensure_models_downloaded(sadtalker_dir)

    # Ensure Python deps
    _ensure_python_dependencies(sadtalker_dir)

    # Ensure results directory
    results_dir_path = Path(results_dir)
    results_dir_path.mkdir(parents=True, exist_ok=True)

    # Decide on device flag for macOS CPU by default
    if cpu is None:
        cpu = platform.system() == "Darwin"

    cmd = [
        _get_python_exec(),
        "inference.py",
        "--driven_audio", narration_wav,
        "--source_image", avatar_image,
        "--result_dir", str(results_dir_path),
        "--preprocess", preprocess,
        "--size", str(size),
    ]
    if still:
        cmd.append("--still")
    if enhancer:
        cmd.extend(["-\-enhancer".replace("\\", ""), enhancer])
    if cpu:
        cmd.append("--cpu")

    result = subprocess.run(cmd, cwd=sadtalker_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"SadTalker inference failed: {result.stderr or result.stdout}")

    # inference.py moves the final video to results/<timestamp>.mp4
    mp4s = sorted((results_dir_path).glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp4s:
        # Fallback: search latest timestamped subdir for enhanced result
        subdir_mp4s = sorted(results_dir_path.rglob("*enhanced.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not subdir_mp4s:
            raise RuntimeError("SadTalker produced no mp4 output in results directory")
        return str(subdir_mp4s[0])
    return str(mp4s[0])


def overlay_on_background(background_video: str, talking_head_video: str, output_path: str,
                          overlay_width: int = 400, bottom_margin: int = 20) -> str:
    """Overlay the talking head video bottom-center on a background using ffmpeg."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    filter_complex = f"[1:v]scale={overlay_width}:-1[fg];[0:v][fg]overlay=(W-w)/2:H-h-{bottom_margin}:format=auto"
    cmd = [
        "ffmpeg", "-y",
        "-i", background_video,
        "-i", talking_head_video,
        "-filter_complex", filter_complex,
        "-map", "0:a?", "-map", "1:a?", "-map", "0:v", "-map", "1:v",
        "-shortest",
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed: {result.stderr}")
    return output_path


def create_talking_head_with_background(
    narration_wav: str,
    avatar_image: str,
    background_video: Optional[str] = None,
    results_dir: str = "results",
    output_path: str = "generated_videos/final_video.mp4"
) -> str:
    """
    Generate a SadTalker talking head from audio+image and optionally overlay on background.
    """
    talking_head = run_sadtalker(narration_wav, avatar_image, results_dir)

    if background_video and Path(background_video).exists():
        return overlay_on_background(background_video, talking_head, output_path)

    # If no background, just re-encode to our standard output location/format
    Path(Path(output_path).parent).mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", talking_head,
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg encode failed: {result.stderr}")
    return output_path


def create_talking_head_from_script(
    script_text: str,
    avatar_image: str,
    background_video: Optional[str] = None,
    speaker_gender: str = "unknown",
    results_dir: str = "results",
    output_path: str = "generated_videos/final_video.mp4"
) -> str:
    """Generate ElevenLabs/local voice audio from script and run SadTalker pipeline."""
    # Generate audio via existing voice tool helpers
    try:
        from tools.voice_tool import create_natural_voiceover, create_voiceover
        try:
            narration_wav = create_natural_voiceover(script_text)
        except Exception:
            narration_wav = create_voiceover(script_text, speaker_gender=speaker_gender)
    except Exception as e:
        raise RuntimeError(f"Voice generation failed: {e}")

    return create_talking_head_with_background(
        narration_wav=narration_wav,
        avatar_image=avatar_image,
        background_video=background_video,
        results_dir=results_dir,
        output_path=output_path
    )


