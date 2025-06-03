SELF  := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

ENV_RUN      = hatch env run -e $(1) --
ENV_IONOS_DEFAULT := $(shell hatch env find ionos-default)

ifdef ENV_IONOS_DEFAULT
$(ENV_IONOS_DEFAULT):
	hatch env create ionos-default
endif

.PHONY: submodule-requirements infra pre site main verification ionos

submodule-requirements:
	$(MAKE) -C submodule-one-deploy-validation requirements

# Explicitly expose these targets to the parent Makefile.
infra pre site main verification:
	$(MAKE) -C submodule-one-deploy-validation I=$(SELF)/inventory/ionos.yml $@

ionos: $(ENV_IONOS_DEFAULT)
	cd $(SELF)/ && \
	$(call ENV_RUN,ionos-default) ansible-playbook $(SELF)/playbooks/ionos.yml
