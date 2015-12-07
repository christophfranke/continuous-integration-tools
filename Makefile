JS_FILE = $(BUILD)/main.js
CSS_FILE = $(BUILD)/style.css
LESS_FILE = $(SRC)/less/style.less

JS_SRC = $(wildcard $(SRC)/js/*.js)
LESS_SRC = $(wildcard $(SRC)/less/*.less)

js: $(JS_FILE)

$(JS_FILE): $(JS_SRC)
	minify --output $(JS_FILE) $(JS_SRC)

less: $(CSS_FILE)

$(CSS_FILE): $(LESS_SRC)
	lessc $(LESS_FILE) $(CSS_FILE)

all: js less
