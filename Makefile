SELF  := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

submodule-requirements:
	$(MAKE) -C submodule-one-deploy-validation requirements

# Explicitly expose these targets to the parent Makefile.
infra pre ceph site main verification:
	$(MAKE) -C submodule-one-deploy-validation I=$(SELF)/inventory/ionos.yml $@

