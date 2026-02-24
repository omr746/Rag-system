# Predictive Maintenance 
This project proposes the design and implementation of an AI-based Predictive
Maintenance (PdM) platform specifically tailored for industrial pumps, one of the most
critical and failure-prone components in manufacturing, water treatment, and energy
sectors.
The system predicts potential failures, classifies fault types, estimates Remaining Useful
Life (RUL), and — unlike traditional PdM systems — provides reasoning explanations to
clarify why a failure is expected, not just when.
The solution integrates real-time sensor data acquisition, data-gap handling, multi-model
AI analysis, and an interactive dashboard capable of visualizing complex relationships
among features.
This enables engineers and technicians to make proactive, data-driven maintenance
decisions with minimal AI expertise.
Although the first implementation focuses on industrial pumps, the architecture is
designed to be scalable, enabling future generalization to motors, compressors, and
turbines.
## Requreiments
-Python 3.8 or later
#### Install python with miniconda
1) Downaload and install from [here](https://www.anaconda.com/docs/getting-started/miniconda/main)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag python=3.8
```
3) Activate the environment:
```bash
$ conda activate rag-app
```
4) (Optional) Setup you command line interface for better readability
```bash
$ export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```
# Installation
### Install the required packages
```bash
$ pip install -r requirements.txt
```
### Setup the environment variables
```bash
$ cp .env.example .env
```
Set your environment variables in the .env file. Like OPENAI_API_KEY value.
## Run Fast api server 
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```