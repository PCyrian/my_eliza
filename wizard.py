import subprocess
import pkg_resources
import os

dependencies = {
    "Babel": "2.15.0",
    "Cython": "3.0.10",
    "Markdown": "3.6",
    "MarkupSafe": "2.1.5",
    "PyAudio": "0.2.14",
    "PyYAML": "6.0.1",
    "SudachiDict-core": "20240409",
    "SudachiPy": "0.6.8",
    "TTS": "0.22.0",
    "Unidecode": "1.3.8",
    "absl-py": "2.1.0",
    "aiohttp": "3.9.5",
    "aiosignal": "1.3.1",
    "annotated-types": "0.7.0",
    "anyascii": "0.3.2",
    "anyio": "4.4.0",
    "async-timeout": "4.0.3",
    "attrs": "23.2.0",
    "audioread": "3.0.1",
    "backoff": "2.2.1",
    "bangla": "0.0.2",
    "blinker": "1.8.2",
    "blis": "0.7.11",
    "bnnumerizer": "0.0.2",
    "bnunicodenormalizer": "0.1.7",
    "catalogue": "2.0.10",
    "certifi": "2024.2.2",
    "cffi": "1.16.0",
    "charset-normalizer": "3.3.2",
    "click": "8.1.7",
    "cloudpathlib": "0.16.0",
    "colorama": "0.4.6",
    "confection": "0.1.4",
    "contourpy": "1.2.1",
    "coqpit": "0.0.17",
    "customtkinter": "5.2.2",
    "cycler": "0.12.1",
    "cymem": "2.0.8",
    "darkdetect": "0.8.0",
    "dateparser": "1.1.8",
    "decorator": "5.1.1",
    "distro": "1.9.0",
    "docopt": "0.6.2",
    "einops": "0.8.0",
    "encodec": "0.1.1",
    "exceptiongroup": "1.2.1",
    "filelock": "3.14.0",
    "flask": "3.0.3",
    "fonttools": "4.52.4",
    "frozenlist": "1.4.1",
    "fsspec": "2024.5.0",
    "g2pkk": "0.1.2",
    "geographiclib": "2.0",
    "geopy": "2.4.1",
    "grpcio": "1.64.0",
    "gruut": "2.2.3",
    "gruut-ipa": "0.13.0",
    "gruut-lang-de": "2.0.0",
    "gruut-lang-en": "2.0.0",
    "gruut-lang-es": "2.0.0",
    "gruut-lang-fr": "2.0.2",
    "h11": "0.14.0",
    "hangul-romanize": "0.1.0",
    "httpcore": "1.0.5",
    "httpx": "0.27.0",
    "huggingface-hub": "0.23.2",
    "idna": "3.7",
    "importlib-metadata": "7.1.0",
    "importlib-resources": "6.4.0",
    "inflect": "7.2.1",
    "intel-openmp": "2021.4.0",
    "itsdangerous": "2.2.0",
    "jamo": "0.4.1",
    "jieba": "0.42.1",
    "jinja2": "3.1.4",
    "joblib": "1.4.2",
    "jsonlines": "1.2.0",
    "keyboard": "0.13.5",
    "kiwisolver": "1.4.5",
    "langcodes": "3.4.0",
    "language-data": "1.2.0",
    "lazy-loader": "0.4",
    "librosa": "0.10.0",
    "llvmlite": "0.42.0",
    "marisa-trie": "1.1.1",
    "matplotlib": "3.8.4",
    "mkl": "2021.4.0",
    "more-itertools": "10.2.0",
    "mpmath": "1.3.0",
    "msgpack": "1.0.8",
    "multidict": "6.0.5",
    "murmurhash": "1.0.10",
    "mutagen": "1.47.0",
    "networkx": "2.8.8",
    "nltk": "3.8.1",
    "num2words": "0.5.13",
    "numba": "0.59.1",
    "numpy": "1.22.0",
    "openai": "1.30.4",
    "opencage": "2.4.0",
    "packaging": "24.0",
    "pandas": "1.5.3",
    "pillow": "10.3.0",
    "pip": "24.0",
    "platformdirs": "4.2.2",
    "pooch": "1.8.1",
    "preshed": "3.0.9",
    "protobuf": "5.27.0",
    "psutil": "5.9.8",
    "pycparser": "2.22",
    "pydantic": "2.7.2",
    "pydantic-core": "2.18.3",
    "pydub": "0.25.1",
    "pygame": "2.5.2",
    "pynndescent": "0.5.12",
    "pyparsing": "3.1.2",
    "pypinyin": "0.51.0",
    "pysbd": "0.3.4",
    "python-crfsuite": "0.9.10",
    "python-dateutil": "2.9.0.post0",
    "pytz": "2024.1",
    "regex": "2024.5.15",
    "requests": "2.32.2",
    "safetensors": "0.4.3",
    "scikit-learn": "1.5.0",
    "scipy": "1.11.4",
    "setuptools": "68.2.0",
    "six": "1.16.0",
    "smart-open": "6.4.0",
    "sniffio": "1.3.1",
    "soundfile": "0.12.1",
    "soxr": "0.3.7",
    "spacy": "3.7.4",
    "spacy-legacy": "3.0.12",
    "spacy-loggers": "1.0.5",
    "srsly": "2.4.8",
    "sympy": "1.12",
    "tbb": "2021.12.0",
    "tensorboard": "2.16.2",
    "tensorboard-data-server": "0.7.2",
    "thinc": "8.2.3",
    "threadpoolctl": "3.5.0",
    "tokenizers": "0.19.1",
    "torch": "2.3.0",
    "torchaudio": "2.3.0",
    "torchvision": "0.18.0",
    "tqdm": "4.66.4",
    "trainer": "0.0.36",
    "transformers": "4.41.1",
    "typeguard": "4.3.0",
    "typer": "0.9.4",
    "typing-extensions": "4.12.0",
    "tzdata": "2024.1",
    "tzlocal": "5.2",
    "umap-learn": "0.5.6",
    "urllib3": "2.2.1",
    "wasabi": "1.1.2",
    "weasel": "0.3.4",
    "werkzeug": "3.0.3",
    "wheel": "0.41.2",
    "yarl": "1.9.4",
    "zipp": "3.19.0"
}


def check_and_install(package, version):
    try:
        pkg_resources.get_distribution(f"{package}=={version}")
        return f"{package} is already installed."
    except pkg_resources.DistributionNotFound:
        subprocess.check_call(["pip", "install", f"{package}=={version}"])
        return f"{package} has been installed."


def install_dependencies():
    results = []
    try:
        for package, version in dependencies.items():
            result = check_and_install(package, version)
            results.append(result)
        return "\n".join(results), True
    except Exception as e:
        return str(e), False


def print_warning(text):
    yellow_color = "\033[93m"
    reset_color = "\033[0m"
    warning_message = f"{yellow_color}[WARNING]{reset_color} {text}"
    print(warning_message)

def check_environment_variables():
    variables_to_check = ["OPENAI_API_KEY"]
    for variable in variables_to_check:
        if not os.getenv(variable):
            warning_text = variable + "env variable not set. Features requiring a" + variable + "will not be available."
            print_warning(warning_text)


def main():
    install_dependencies()
    check_environment_variables()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

input("Press Enter to exit...")