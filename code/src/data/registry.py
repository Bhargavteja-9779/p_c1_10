"""Registry of public datasets: source URL, licence, checksum, citation.

Checksums: Mendeley Data publishes SHA-256 hashes, which are verified on download.
For Eigenvector files no hash is published; the hash observed at first download is
recorded in data/MANIFEST.json and verified on every later download.
"""
DATASETS = {
    "mango_v3": {
        "url": "https://data.mendeley.com/public-files/datasets/46htwnp833/files/10975117-717b-4504-a372-7845b4c42237/file_downloaded",
        "filename": "MangoDMC_NIR_Data_v3.csv",
        "sha256": "1e0e450417ed96b47b3808556706afa84a2e6441a76e380a8b64b18d85fddee1",
        "size": 35273684,
        "licence": "CC BY 4.0",
        "doi": "10.17632/46htwnp833",
        "citation": "Anderson N.T., Walsh K.B., Subedi P.P., Walsh J. Mango DMC and NIR spectra. Mendeley Data (v6, 2026). doi:10.17632/46htwnp833",
        "notes": "Each fruit scanned twice; random splits leak replicates (dataset authors' warning). Season-based train/test as in Anderson et al. 2020.",
    },
    "mango_v4": {
        "url": "https://data.mendeley.com/public-files/datasets/46htwnp833/files/747b2613-4d0a-4628-8aaf-8fc5547d286e/file_downloaded",
        "filename": "MangoDMC_NIR_Data_v4.csv",
        "sha256": "367c377255c350f322387236ed121629807055baa3f02aeaf5a76fe9ada518b6",
        "size": 259972844,
        "licence": "CC BY 4.0",
        "doi": "10.17632/46htwnp833",
        "citation": "Anderson N.T., Walsh K.B., Subedi P.P., Walsh J. Mango DMC and NIR spectra. Mendeley Data (v6, 2026). doi:10.17632/46htwnp833",
        "notes": "Adds instruments and seasons (J. Walsh thesis 2024); subset scanned at 15/25/35 C.",
    },
    "corn": {
        "url": "https://eigenvector.com/wp-content/uploads/2019/06/corn.mat_.zip",
        "filename": "corn.mat_.zip",
        "sha256": None,
        "licence": "Publicly distributed by Eigenvector Research for benchmarking (no explicit licence stated); originally Cargill.",
        "citation": "Corn data set, 80 samples on 3 NIR instruments (m5, mp5, mp6), Eigenvector Research, https://eigenvector.com/resources/data-sets/",
        "notes": "80 samples x 700 channels (1100-2498 nm); moisture, oil, protein, starch; NBS glass standards.",
    },
    "tablets": {
        "url": "https://eigenvector.com/wp-content/uploads/2019/06/nir_shootout_2002.mat_.zip",
        "filename": "nir_shootout_2002.mat_.zip",
        "sha256": None,
        "licence": "IDRC 2002 Shootout data, publicly distributed by Eigenvector Research (no explicit licence stated).",
        "citation": "IDRC 2002 Software Shootout pharmaceutical tablets, 654 tablets on two NIR spectrometers, Eigenvector Research.",
        "notes": "Calibration/validation/test partitions as distributed.",
    },
    "diesel": {
        "url": "https://eigenvector.com/wp-content/uploads/2019/06/SWRI_Diesel_NIR_CSV.zip",
        "filename": "SWRI_Diesel_NIR_CSV.zip",
        "sha256": None,
        "licence": "Publicly distributed by Eigenvector Research with SWRI permission (no explicit licence stated).",
        "citation": "SWRI diesel fuel NIR data (bp50, cetane, density, freezing point, total aromatics, viscosity), Eigenvector Research.",
        "notes": "Multiple fuel properties per spectrum.",
    },
}
