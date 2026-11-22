SHELL := /bin/sh

SPEC ?= ../../../isa/v0.58/linxisa-v0.58.json
UOP_ROOT ?= ../../../isa/v0.58/uop_classification_v0.58
GEN_DIR ?= src/generated
DOC ?= src/linxisa-isa-manual.adoc

BUILD_DIR ?= build
PDF ?= $(BUILD_DIR)/linxisa-isa-manual.pdf
HTML ?= $(BUILD_DIR)/linxisa-isa-manual.html

.PHONY: all pdf html gen check-generated clean bundle-check

all: pdf

bundle-check:
	@command -v bundle >/dev/null 2>&1 || (echo "ERROR: bundler not found (expected 'bundle' in PATH)"; exit 1)

gen:
	@mkdir -p $(GEN_DIR)/encodings $(GEN_DIR)/instructions
	python3 ../../../tools/isa/gen_encoding_svg.py --spec $(SPEC) --out-dir $(GEN_DIR)/encodings
	python3 ../../../tools/isa/gen_manual_adoc.py --spec $(SPEC) --out-dir $(GEN_DIR) --svg-dir $(GEN_DIR)/encodings
	python3 ../../../tools/isa/gen_instruction_fragments.py --spec $(SPEC) --uop-root $(UOP_ROOT) --out-dir $(GEN_DIR)/instructions --enc-rel-dir encodings
	python3 ../../../tools/isa/gen_ssr_adoc.py --spec $(SPEC) --out-dir $(GEN_DIR)

check-generated:
	python3 ../../../tools/isa/gen_encoding_svg.py --spec $(SPEC) --out-dir $(GEN_DIR)/encodings --check
	python3 ../../../tools/isa/gen_manual_adoc.py --spec $(SPEC) --out-dir $(GEN_DIR) --svg-dir $(GEN_DIR)/encodings --check
	python3 ../../../tools/isa/gen_instruction_fragments.py --spec $(SPEC) --uop-root $(UOP_ROOT) --out-dir $(GEN_DIR)/instructions --enc-rel-dir encodings --check

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

pdf: bundle-check gen | $(BUILD_DIR)
	bundle install --path vendor/bundle
	bundle exec asciidoctor-pdf -D $(BUILD_DIR) -o $(notdir $(PDF)) $(DOC)
	@echo "Built $(PDF)"

html: bundle-check gen | $(BUILD_DIR)
	bundle install --path vendor/bundle
	bundle exec asciidoctor -D $(BUILD_DIR) -o $(notdir $(HTML)) $(DOC)
	@echo "Built $(HTML)"

clean:
	rm -rf $(BUILD_DIR) $(GEN_DIR) vendor/bundle .bundle

.PHONY: html-reference check-html-reference

html-reference:
	python3 ../../../tools/isa/gen_html_reference.py --out $(BUILD_DIR)/instruction-reference --zip $(BUILD_DIR)/linxisa-0.59.1-html.zip

check-html-reference:
	python3 ../../../tools/isa/gen_html_reference.py --check --out $(BUILD_DIR)/instruction-reference
	python3 ../../../tools/isa/check_html_reference.py --site $(BUILD_DIR)/instruction-reference
	python3 ../../../tools/isa/check_manual_structure.py --site $(BUILD_DIR)/instruction-reference
	python3 ../../../tools/isa/check_manual_authored.py --site $(BUILD_DIR)/instruction-reference
	python3 ../../../tools/isa/check_manual_site_quality.py --site $(BUILD_DIR)/instruction-reference
