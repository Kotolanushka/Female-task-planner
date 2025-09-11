class Translator {
    constructor() {
        this.translations = new Map();
    }

    addTranslation(key, value) {
        this.translations.set(key, value);
    }

    gettext(key) {
        return this.translations.get(key) || key;
    }
}

const translator = new Translator();

translator.addTranslation('Январь', 'January');
translator.addTranslation('Февраль', 'February');
translator.addTranslation('Март', 'March');
translator.addTranslation('Апрель', 'April');
translator.addTranslation('Май', 'May');
translator.addTranslation('Июнь', 'June');
translator.addTranslation('Июль', 'July');
translator.addTranslation('Август', 'August');
translator.addTranslation('Сентябрь', 'September');
translator.addTranslation('Октябрь', 'October');
translator.addTranslation('Ноябрь', 'November');
translator.addTranslation('Декабрь', 'December');