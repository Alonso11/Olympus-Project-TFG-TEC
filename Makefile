# Makefile for SRS Rover Olympus LaTeX Project

# Configuration
MAIN = main
SOURCE_DIR = sections
BUILD_DIR = .
PDF_VIEWER = xdg-open # Change to 'open' on macOS or 'evince' depending on your system

# Tools
LATEX = pdflatex
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

# Find all source files to track changes
SOURCES = $(MAIN).tex $(wildcard $(SOURCE_DIR)/*.tex)

.PHONY: all clean view help

all: $(MAIN).pdf ## Generate the PDF (default)

$(MAIN).pdf: $(SOURCES)
	@echo "Generating PDF (Pass 1)..."
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Generating PDF (Pass 2 for references/TOC)..."
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Done! PDF generated: $(MAIN).pdf"

view: $(MAIN).pdf ## Open the generated PDF
	$(PDF_VIEWER) $(MAIN).pdf &

clean: ## Remove temporary build files
	@echo "Cleaning up..."
	rm -f *.aux *.log *.out *.toc *.pdf *.nav *.snm *.vrb *.fls *.fdb_latexmk *.synctex.gz
	rm -f $(SOURCE_DIR)/*.aux
	@echo "Cleanup complete."

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
