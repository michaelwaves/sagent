# Sagent - Useful AI Agent for SFold

[Website](https://aso-frontend.vercel.app/)

## Quickstart
0. Have your Sagent Key in `./sagent/` as "sagent-key.pem"
1. Install [Anaconda](https://www.anaconda.com/download/success)
2. Based on [NEAR AI GitHub](https://github.com/nearai/nearai?tab=readme-ov-file#log-in),
create [NEAR AI account](https://wallet.near.org/) (speaker rec Meteor)

```
chmod 400 "sagent-key.pem"
ssh -i "sagent-key.pem" admin@ec2-18-216-25-202.us-east-2.compute.amazonaws.com

conda create -n useful_agent python=3.10 -y
conda activate useful_agent
pip install nearai
```
## Literature embeddings
The literature on Sfold and RNA sequences is in /literature. We use xtrace to create a knowlege base in vectorstore.ipynb

## Useful Links

- [Submission Form](https://docs.google.com/forms/d/e/1FAIpQLSebTq_Md0PwklTTNhr-zdidkk6Y45VeQ_kefyJrqJGnaVjsaA/viewform)
- [Bounty Notion Page](https://near-foundation.notion.site/Useful-Agent-Hackathon-Bounty-Board-1b3da22d7b6480049c88d19c52c16260)
- [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/)
- [Sfold site](https://sfold.wadsworth.org/cgi-bin/index.pl)

## SFold Docs

[Original Project](https://github.com/Ding-RNA-Lab/Sfold)

This repository contains the Sfold suite of tools.

To download the source code and executables, click on the green "Code" button.

To install and load sfold, read the RUNNING_SFOLD file in this directory.

The starmir scripts for binding site prediction and ranking are in the subfolder
"STarMir".

These programs only run under Linux.  It is probable they could be compiled
and run under other *nix operating systems.


