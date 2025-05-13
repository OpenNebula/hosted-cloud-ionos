SHELL := $(shell which bash)
SELF  := $(patsubst %/,%,$(dir $(abspath $(firstword $(MAKEFILE_LIST)))))

ENV_RUN      = hatch env run -e $(1) --
ENV_DEFAULT := $(shell hatch env find default)

I         ?= $(SELF)/inventory/example.yml
INVENTORY ?= $(I)

T    ?=
TAGS ?= $(T)

S         ?=
SKIP_TAGS ?= $(S)

V       ?= vv
VERBOSE ?= $(V)

ONE_DEPLOY_URL ?= git+https://github.com/OpenNebula/one-deploy.git,master

export

# Make sure we source ANSIBLE_ settings from ansible.cfg exclusively.
unexport $(filter ANSIBLE_%,$(.VARIABLES))

.PHONY: all

all: main

.PHONY: infra pre site main

infra pre site main: _TAGS      := $(if $(TAGS),-t $(TAGS),)
infra pre site main: _SKIP_TAGS := $(if $(SKIP_TAGS),--skip-tags $(SKIP_TAGS),)
infra pre site main: _VERBOSE   := $(if $(VERBOSE),-$(VERBOSE),)
infra pre site main: _ASK_VAULT := $(if $(findstring $$ANSIBLE_VAULT;,$(file < $(INVENTORY))),--ask-vault-pass,)

ifdef ENV_DEFAULT
$(ENV_DEFAULT):
	hatch env create default
endif

infra pre site main: $(ENV_DEFAULT)
	cd $(SELF)/ && \
	$(call ENV_RUN,default) ansible-playbook $(_VERBOSE) -i $(INVENTORY) $(_ASK_VAULT) $(_TAGS) $(_SKIP_TAGS) $(SELF)/playbooks/$@.yml


.PHONY: requirements requirements-hatch requirements-galaxy clean-requirements

requirements: requirements-hatch requirements-galaxy

requirements-hatch: $(SELF)/pyproject.toml $(ENV_DEFAULT)

requirements-galaxy: $(ENV_DEFAULT)
	$(call ENV_RUN,default) ansible-galaxy collection install --upgrade $(ONE_DEPLOY_URL)

clean-requirements:
	$(if $(ENV_DEFAULT),hatch env remove default,)

.PHONY: lint-ansible

lint-ansible: $(ENV_DEFAULT)
	cd $(SELF)/ && $(call ENV_RUN,default) ansible-lint roles/ playbooks/
