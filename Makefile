
MAIN_JS = main.js
MAIN_JS_MAP = $(MAIN_JS).map
JS_FILE = $(BUILD)/$(MAIN_JS)
JS_MAP_FILE = $(BUILD)/$(MAIN_JS_MAP)

CSS_FILE = $(BUILD)/style.css
LESS_FILE = $(SRC)/less/style.less

JS_SRC = $(shell find $(SRC)/js -name "*.js")
LESS_SRC = $(shell find $(SRC)/less -name "*.less")

COMPILER = compiler.jar

ESCAPED_SRC_DIR = $(shell echo $(SRC)|sed 's\#/\#\\/\#g')
ESCAPED_SRC_URL = $(shell echo /$(SRC_URL)|sed 's\#/\#\\/\#g')

ESCAPED_BUILD_DIR = $(shell echo $(BUILD)|sed 's\#/\#\\/\#g')
ESCAPED_BUILD_URL = $(shell echo /$(BUILD_URL)|sed 's\#/\#\\/\#g')

js: $(JS_FILE) $(JS_MAP_FILE)


$(JS_FILE) $(JS_MAP_FILE): $(JS_SRC)
	java -jar $(COMPILER) --js $(JS_SRC) --create_source_map $(JS_MAP_FILE) --js_output_file $(JS_FILE)
	echo "//# sourceMappingURL=$(MAIN_JS_MAP)" >> $(JS_FILE)
	sed -i '' -e 's/$(ESCAPED_SRC_DIR)/$(ESCAPED_SRC_URL)/g' $(JS_MAP_FILE)
	sed -i '' -e 's/$(ESCAPED_BUILD_DIR)/$(ESCAPED_BUILD_URL)/g' $(JS_MAP_FILE)

less: $(CSS_FILE)

$(CSS_FILE): $(LESS_SRC)
	lessc --source-map --verbose --clean-css $(LESS_FILE) $(CSS_FILE)

all: js less
