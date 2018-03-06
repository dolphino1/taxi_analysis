run_tests:
	@echo "Running all tests ..."
	python `which nosetests`

run_tests_with_coverage:
	@echo "Running all tests with coverage ..."
	python `which nosetests` --with-coverage --cover-package=.

preprocess_data:
	@echo "Calculating preprocessed data ..."
	python src/data_preprocess/make_calculations.py

create_environment:
	@echo "Creating Environment"
	conda env create -f environment.yml

start_environment:
	@echo "run source activate sot-env in your terminal"

delete_environment:
	@echo "removing environment from anaconda"
	conda remove --name sot-env --all


