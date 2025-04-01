# Survey_Airport
Repository for storing data cleaning, processing, expansion, and summarization scripts for a survey conducted at SDIA in the Fall of 2025.  

# Organization
The data manipulation procedures are stored in a series of Jupyter notebooks (with a single R notebook) in the `/notebooks` directory. The data cleaning and processing are aided by a [Pydantic](https://docs.pydantic.dev/latest/) data model, which is stored in the `data_model` folder. [MkDocs](https://www.mkdocs.org/) is used to create [API documentation](https://sandag.github.io/Survey_Airport/index.html) of the data model, which provides one method to quickly query the data model, which serves as a data dictionary. The `docs` directory contains the markdown files used in the API documentation website, which is configured via the `mkdocs.yml` file and created by GitHub using GitHub Actions (see `/.github/workflows/docs.yml`).

# Environments
1. The Python environment used in the GitHub Actions to create the API documentation website is specified in the `/.github/workflows/docs.yml` file with the requirements defined in the `docs_requirements.txt` file. 
2. The Python environment used to run the Jupyter notebooks is Python 3.12, with the requirements defined in the `requirements.txt` file. See the `create-env.bat` file for commands needed to create a virtual environment to run the notebooks. If using VS Code and you cannot find the kernel in the list of options, try running the `add_kernel_to_jupyter.bat` instructions and then restarting VS Code. 
3. The R environment used to run the single R notebook is R 2023.12.1+402. The notebook uses only the `tidyverse` and `yaml` third-party libraries. 

# Data Processing Sequence
The steps to process the data are as follows:

### 1. `/notebooks/01-make-clean-data-from-raw-data.ipynb`
This Python notebooks starts with the "raw" data delivered by the field team. The raw data is expected to be stored in the `/data/external/etc` folder as Excel files. These files are not checked into GitHub. This notebook engaged in a bit of hand-to-hand combat to do some cleaning up of the data and joining survey data collected at different stages in the process. 

A dictionary is used in this script to rename variables. See `/data/processed/revised_names.csv`. This moves the data from the variable names used by the field team, which are useful for keeping track of question sequencing, and the variable names we want in the end data product. 

The data model expects the data to be serialized in a specific manner. Specifically, it expects that the data is a list of persons who have made trips to the airport. In the data model, each `Respondent` has a `Trip`. This notebook serializes the data with this code:

```{python}
respondent_list = add_list_objects(
        trips_df.to_dict(orient="records"),  #child list
        "respondentid", # child key
        persons_df.to_dict(orient="records"), # parent list
        "respondentid", # parent key
        "trip", # parent var
    )
```

The Python Pydantic package makes validating data with a data model straightforward. The code that does this looks like this:

```{python}
employee_list = []
arriving_air_passenger_resident_list = []
arriving_air_passenger_visitor_list = []
departing_air_passenger_resident_list = []
departing_air_passenger_visitor_list = []
other_list = []
failed_records = []

for respondent in respondent_list:
     market_segment = respondent["marketsegment"]
     try:
        if market_segment == e.Type.EMPLOYEE:
            ev = Employee(** respondent)
            employee_list.append(ev)
        elif market_segment == e.Type.PASSENGER:
             passenger_segment= respondent["passenger_segment"]
             if passenger_segment == e.PassengerSegment.RESIDENT_ARRIVING:
                    apr = ArrivingPassengerResident(** respondent)
                    arriving_air_passenger_resident_list.append(apr)
             elif passenger_segment == e.PassengerSegment.VISITOR_ARRIVING:
                    apv = ArrivingPassengerVisitor(** respondent)
                    arriving_air_passenger_visitor_list.append(apv)
             elif passenger_segment == e.PassengerSegment.RESIDENT_DEPARTING:
                    dpr = DepartingPassengerResident(** respondent)
                    departing_air_passenger_resident_list.append(dpr)
             elif passenger_segment == e.PassengerSegment.VISITOR_DEPARTING:
                    dpv = DepartingPassengerVisitor(** respondent)
                    departing_air_passenger_visitor_list.append(dpv)
             else:
                    rv = Respondent(** respondent)
                    other_list.append(rv)

        else:
            rv = Respondent(** respondent)
            other_list.append(rv)
            
     except ValidationError as err:
            respondent['error_flag'] = 'failed'
            respondent['error_message'] = str(err)
            failed_records.append(respondent) 


failed_df = pd.DataFrame(failed_records)
failed_df.head()
```

This code first determines whether or not the relevant record is an `Employee` or an `ArrivingPassengerResident`, `ArrivingPassengerVisitor`, `DepartingPassengerResident` or a `DepartingPassengerVisitor` (all of which are based on the `Respondent` data model class) and then instantiates the relevant data model class. This instantiation does the validation. If the validation is unsuccessful, these "failed" records are stored in a separate data frame.

The sampling frame of the survey was passengers departing the airport. To augment the data, we create synthetic records of travelers leaving the airport using data from the survey. The method for doing this is stored in `/data_model/utils.py`.

The rest of the steps in the notebook "un-serialize" the data to create the expected flat file, use the enumerated variables stored in `enums.py` to label the data, and give each record a unique identifier. The outcome of this process is a csv file stored in `/data/processed` directory called `data_model_output.csv`.

### 2. `/notebooks/02-survey-expansion.Rmd` 
The survey expansion is done in R. It starts with the `data_model_output.csv` and uses the following files:

a. A `yaml` configuration file. See `/data/interim/expansion_config_*.yml`.
b. A `csv` controls file. See `/data/interim/expansion_controls_*.csv`. This file is specified in the configuration file. The controls are the expansion targets.
c. A `csv` controls expression file. See `/data/interim/expansion_controls_expressions_*.csv`. This file is specified in the configuration file. The expressions show how to compute the controls from the survey data. 

Configuration and control files are in place for two expansions: one using only departing passengers and employees; and one using departing passengers, arriving passengers (including synthetic records), and employees. The relevant files are labeled as either `departing_only` or `departing_and_arriving`. 

The expansion uses an iterative optimization methodology to fit each control by adjusting the record weights. 

Users can toggle the expansion by adjusting the configuration file in this line of code:

```{R}
config_file <- paste0(interim_dir, "expansion_config_departing_and_arriving.yaml")
```

Please also note that the working directory is set in the code to be the procedures robust against different type of execution types (e.g., running line by line, "knitting" to create an HTML record of the script). Users will need to adjust the working directory prior to executing the code locally. 

The script generates numerous diagnostic data, as well as a `csv` file that contains the expansion weight for each record, with a separate file for each expansion approach. 
### 3. `/notebooks/03-merge-weights-to-data.ipynb`
This notebook attaches populates the `weight` field in the `data_model_output.csv` file generated in step 1 using the `weights_only_file` generated in step 2.

### 4. `/notebooks/04-create-variable-summaries.ipynb`
This notebook creates lightly formatted variable summaries in Microsoft Word format. It joins the data model output from step 1 with the weights generated in step 2. The summaries currently use the departing only set of weights. 

### 5. `/notebooks/05-mode-summaries-by-date.ipynb`
This is a utility notebook used for doing *ad hoc* investigation of mode choice outcomes across the survey period. It is not part of the core data processing workflow.

### 6. `/notebooks/06-compare-pilot-and-original.ipynb`
This is a utility notebook used to compare the outcomes from the pilot phase of the survey and the non-pilot phase of the survey. 

### 7. `/notebooks/07-create-zonal-distribution-summaries.ipynb`
This notebooks generates the distribution of resident passengers by PMSA and Municipal Zones. It generates 4 summaries, number of travelers and travel parties, weighted and unweighted for each zonal system and saves it as an excel file. See `/reports/zonal_distribution_resident_passengers.xlsx`.

### 8. `/notebooks/08-make-zonal-distribution-maps.ipynb`
This notebooks generates maps using shapefiles of PMSA and Municipal Zones and plotting the trip origins for resident departing passengers (or destinations for resident arriving passengers).


### 10. `/notebooks/10-make-excel-data-dictionary-from-data-model.ipynb`
The data model can be examined and queried via the [API documentation](https://sandag.github.io/Survey_Airport/index.html). For many users, this will be the preferred way to examine variable definitions and response options. Others may prefer a more conventional spreadsheet. This script creates a Microsoft Excel spreadsheet from the data model. This allows users to examine a data dictionary in Excel, while maintaining a single source of truth (the data model). See `/reports/data_dictionary.xlsx`. 

### 11. `/notebooks/11-make-word-document-from-excel-data-dictionary.ipynb`
Users may also want to view the data dictionary as a Microsoft Word file. Having a Word version is also useful for static reports. This script renders the data dictionary created in the previous step as a Word document. See `/reports/data_dictonary.docx`. 

### 12. `/notebooks/12-make-word-document-from-excel-questionnaire.ipynb`
There is no perfect way to archive the survey instrument, as its a web-based instrument with skip logic. Screenshots of the questionnairre have been stored. In this script, an Excel version of the questionnaire is rendered as a Word document for easier review. 

