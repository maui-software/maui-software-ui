<h1 align="center">Maui Software UI</h1>

<p align="center">
   <img src="https://img.shields.io/github/license/maui-software/maui-software-ui?style=flat&logo=opensourceinitiative&logoColor=white&color=1cbd9f" alt="license">
   <img src="https://img.shields.io/github/last-commit/maui-software/maui-software-ui?style=flat&logo=git&logoColor=white&color=1cbd9f" alt="last-commit">
   <img src="https://img.shields.io/github/languages/top/maui-software/maui-software-ui?style=flat&color=1cbd9f" alt="repo-top-language">
   <img src="https://img.shields.io/github/languages/count/maui-software/maui-software-ui?style=flat&color=1cbd9f" alt="repo-language-count">
</p>
<p align="center">Built with the tools and technologies:</p>
<p align="center">
   <img src="https://img.shields.io/badge/Dash-008DE4.svg?style=flat&logo=Dash&logoColor=white" alt="Dash">
   <img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
   <img src="https://img.shields.io/badge/Poetry-60A5FA.svg?style=flat&logo=Poetry&logoColor=white" alt="Poetry">
</p>
<br>

<details><summary>Table of Contents</summary>

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

</details>
<hr>

##  Overview

**Maui Software UI** is a graphical application for **ecoacoustic data analysis and visualization**.  
It provides a user-friendly interface built on top of the `maui-software` library, enabling researchers and practitioners to:  

- Load and organize acoustic datasets.  
- Compute a wide range of ecoacoustic indices.  
- Perform segmentation of audio files.  
- Explore the acoustic environment through rich visualizations.  

With support for both **standard spectrograms** and **false-color spectrograms**, Maui Software UI facilitates deeper insights into large ecoacoustic datasets, assisting in biodiversity monitoring and ecological research.

---

##  Features

- **Intuitive data loading** for ecoacoustic analysis.  
- **Built-in computation of multiple acoustic indices**, essential for ecological studies.  
- **Audio file segmentation** (automatic and manual) for detailed inspection.  
- **Interactive visualizations** including:  
  - Traditional spectrograms  
  - False-color spectrograms for enhanced interpretation  
- **Graphical user interface** developed with Dash for seamless data exploration.  

---
##  Getting Started

###  Prerequisites

Before getting started with maui-software-ui, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Poetry


###  Installation and usage

Install maui-software-ui using one of the following methods:

#### **Build from source**

1. Clone the maui-software-ui repository:
```sh
git clone https://github.com/maui-software/maui-software-ui
```

2. Navigate to the project directory:
```sh
cd maui-software-ui
```

3. Install the project dependencies:

```sh
poetry install
```

4. Run maui-software-ui using the following command:


```sh
poetry run python app.py
```

#### **Download executable**

1. Download the app acccording to your operational system

- **Linux** - ![WIP](https://img.shields.io/badge/status-WIP-yellow)
- **Windows** - ![WIP](https://img.shields.io/badge/status-WIP-yellow)
- **MacOS** - ![WIP](https://img.shields.io/badge/status-WIP-yellow)


---

##  Contributing

- **💬 [Join the Discussions](https://github.com/maui-software/maui-software-ui/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/maui-software/maui-software-ui/issues)**: Submit bugs found or log feature requests for the `maui-software-ui` project.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/maui-software/maui-software-ui
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/maui-software/maui-software-ui/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=maui-software/maui-software-ui">
   </a>
</p>
</details>

---

##  License

This project is protected under the MIT License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/mit) file.

---
