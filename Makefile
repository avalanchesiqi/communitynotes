.PHONY : create_mamba_env
.ONESHELL:

SHELL=/bin/bash
PROJ_NAME=communitynotes
ENV_PATH=$$(mamba info --base)
MAMBA_ACTIVATE=source $$(mamba info --base)/etc/profile.d/mamba.sh ; mamba activate $(PROJ_NAME)
DEPENDENCIES=mamba install -y -c anaconda -c conda-forge -c pytorch -c bioconda -c pytorch snakemake-minimal black isort flake8 pytest neovim snakefmt numpy==1.26.4
pandas==2.2.2 torch==2.1.2 scipy==1.11.4 sklearn==1.0.2 seaborn

create_mamba_env:
	echo "Creating mamba environent at ${ENV_PATH}/envs/${PROJ_NAME} (Delete any existing mamba env with the same name).."
	rm -rf "${ENV_PATH}/envs/${PROJ_NAME}"
	mamba create --force -y -n $(PROJ_NAME) python=3.10
	mamba init
	# $(MAMBA_ACTIVATE) ; pip install pyarrow; $(DEPENDENCIES)