SELF  := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

ENV_RUN      = hatch env run -e $(1) --
ENV_IONOS_DEFAULT := $(shell hatch env find ionos-default)

ifdef ENV_IONOS_DEFAULT
$(ENV_IONOS_DEFAULT):
	hatch env create ionos-default
endif

.PHONY: submodule-requirements deployment validation ionos

submodule-requirements:
	$(MAKE) -C submodule-one-deploy requirements

# Explicitly expose these targets to the parent Makefile.
validation:
	$(MAKE) -C submodule-one-deploy-validation I=$(SELF)/inventory/ionos.yml $@

deployment:
	$(MAKE) -C submodule-one-deploy I=$(SELF)/inventory/ionos.yml main

ionos: $(ENV_IONOS_DEFAULT)
	cd $(SELF)/ && \
	$(call ENV_RUN,ionos-default) ansible-playbook $(SELF)/playbooks/ionos.yml
