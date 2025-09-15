# The Role of Context in Multimodal Chart Interpretation and Retrieval

This repository contains the code, data, and analysis for a two-part thesis investigating how surrounding textual context impacts the ability of multimodal language models to interpret charts and improve information retrieval.

## Project Abstract

Chart and infographic interpretation remains a persistent challenge for multimodal language models (MLLMs), especially in applied settings such as retrieval-augmented generation (RAG). This research investigates whether incorporating surrounding textual context enhances model performance through two complementary studies.

In **Study 1**, a high-capacity MLLM generated interpretations for 61 charts, both with and without their original textual context. A blinded human evaluation found that context-enhanced interpretations scored significantly higher on accuracy, relevance, and completeness, and were strongly preferred by the expert rater.

In **Study 2**, a smaller, local vision-language model generated new interpretations for the same charts. These were used to build two vector databases for a RAG experiment. While not statistically significant, interpretations created with context achieved a higher Top-1 hit rate (93.4% vs. 90.2%), suggesting a modest retrieval benefit even for lightweight models.

Together, these investigations demonstrate that context is a crucial factor for improving the quality and applied utility of chart interpretation in multimodal AI systems.

## Repository Structure

This project is divided into two main directories, each corresponding to a distinct study.

*   `study1/`: Contains all materials for the human evaluation of a large MLLM's chart interpretation capabilities.
*   `study2/`: Contains all materials for the RAG experiment using a local VLM.

## Getting Started

For detailed setup instructions, code documentation, and information on how to run each experiment, please refer to the `README.md` file located within the respective study's directory:

*   [**Instructions for Study 1**](./study1/README.md)
*   [**Instructions for Study 2**](./study2/README.md)