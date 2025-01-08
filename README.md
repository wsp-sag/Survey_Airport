# Survey_Airport
Processing scripts for airport surveys
## Intructions to run processing scripts:
1. Create a virtual environment and install necessary libraries using create-env.bat.
    * Update the Python Path in the batch file before running it
2. Put the raw data in the data/external/etc directory
3. Run 01-make-clean-data-from-raw-data.ipynb to create clean data using raw data using the data model. Use the environment created in step 1 to run the jupyter notebook. This will create a clean file in data/processed/data_model_output.csv.
    * If you cannot find the environment in the jupyter notebook, run the batch file: add_kernel_to_jupyter.bat and restart VS Code.
4. Run other notebooks as required