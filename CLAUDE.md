# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

-   **Start Development:** The `package.json` `start` script currently echoes a message to "Open VS Code and use Specify+". The primary way to interact with and develop this project is through the `Specify+` extension in VS Code.
-   **Build Documentation:** The `package.json` `build` script is a placeholder. To build the Docusaurus site, you would typically run `npm run build` after defining the build steps in `package.json` (e.g., `docusaurus build`).

## High-Level Architecture

This repository contains a Docusaurus-based documentation project for the "Hackathon Book".

-   **`docs/`**: This directory is the core of the documentation.
    -   **`docs/chapters/`**: Contains the individual Markdown files for each chapter of the book.
    -   **`docs/glossary.md`**: Defines key terms used throughout the book.
    -   **`docs/images/`**: Stores static image assets referenced within the documentation.
    -   **`docs/styles/`**: Holds custom CSS or styling specific to the book's presentation.
-   **`src/`**: This directory is currently empty, indicating no custom React components or application-specific logic beyond the Docusaurus framework.
-   **`docusaurus.config.js`**: The main configuration file for the Docusaurus site, controlling aspects like title, navigation, plugins, and themes.
-   **`sidebar.js`**: Defines the structure and order of the documentation sidebar, organizing the chapters and other content.