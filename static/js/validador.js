$(function () {
    todosObligatorios = $('input[required],select[required]');
    for (var i = 0; i < todosObligatorios.length; i++) {
        label = $(todosObligatorios[i]).parents('form').first().find('label[for=' + todosObligatorios[i].id + ']');
        label.html("<label><span class='error'>(*) </span>" + label.text() + " </label>")
    }
});

$('.mayuscula').on("keyup", function () {
    s = this.selectionStart;
    e = this.selectionEnd;
    a = this.value.split(" "), b = "";
    for (n in a) {
        b += " " + a[n].substr(0).toUpperCase();
    }
    this.value = b.substr(1);
    this.selectionStart = s;
    this.selectionEnd = e;
});

$(document).ready(function () {
    $.validator.addClassRules({
        password: {
            notEqual: ".actual_password",
        },
        letras_espacios: {
            letras_espacios: ".letras_espacios",
        },
        letras_caracter: {
            letras_caracter: ".letras_caracter",
        },
        letras_man_min: {
            letras_man_min: ".letras_man_min",
        },
        letras_numeros: {
            letras_numeros: ".letras_numeros",
        },
        pattern: {
            pattern: ".pattern",
        },
    });

    $.validator.addMethod("letras_espacios",
        function (value, element, param) {
            return this.optional(element) || /^[A-Z ]+$/.test(value);
        },
        "Por favor, escribe sólo letras y/o espacios.");

    $.validator.addMethod("letras_caracter",
        function (value, element, param) {
            return this.optional(element) || /^([a-zA-Z].)+$/.test(value);
        },
        "Caractéres no permitidos");

    $.validator.addMethod("letras_man_min",
        function (value, element, param) {
            return this.optional(element) || /^[a-zA-ZáéíóúÁÉÍÓÚñÑ., ]+$/.test(value);
        },
        "Por favor, escribe sólo letras y/o espacios.");

    $.validator.addMethod("letras_numeros",
        function (value, element, param) {
            return this.optional(element) || /^[a-zA-Z0-9áéíóúÁÉÍÓÚ.,\- ]+$/.test(value);
        },
        "Por favor, escribe sólo letras y/o espacios.");

    $.validator.addMethod("solo_numeros",
        function (value, element, param) {
            return this.optional(element) || /^[0-9]+$/.test(value);
        },
        "Por favor, ingresar sólo números");

    $.validator.addMethod("notEqual",
        function (value, element, param) {
            return value !== $(param).val();
        },
        "Por favor, especifique una contraseña diferente a la actual");
    $.validator.addMethod("pattern",
        function (value, element, param) {
            pat = $(element).data("patron");
            if (pat !== null) {
                return this.optional(element) || new RegExp(pat).test(value);
            }
        },
        "Por favor, utilice el formato requerido.");


    $.validator.addMethod("menora", function (value_menor, element, param) {
            var target = $(param);
            var value_mayor = target.val();
            if (value_mayor !== "" && value_menor !== "") {
                if (target.attr("type") === "number" && element.type === "number") {
                    if (isNaN(Number(value_mayor)) || isNaN(Number(value_menor))) {
                        return false;
                    } else {
                        return Number(value_menor) < Number(value_mayor);
                    }
                } else if (target.attr("type") === "date" && element.type === "date") {
                    var inicio = new Date(value_menor);
                    var fin = new Date(value_mayor);
                    if (Object.prototype.toString.call(inicio) === "[object Date]"
                        && Object.prototype.toString.call(fin) === "[object Date]") {
                        // it is a date
                        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
                            return false;
                        } else {
                            return inicio < fin;
                        }
                    } else {
                        // no es fecha. valido o no? return true o false?
                        return false;
                    }

                } else if (target.attr("type") === "text" && element.type === "text") {
                    return value_menor < value_mayor;
                }
            }
            return true;

        },
        "Por favor, especifique un valor menor a fin ");

    $.validator.addMethod("mayora", function (value_mayor, element, param) {
            var target = $(param);
            var value_menor = target.val();
            if (value_mayor !== "" && value_menor !== "") {
                if (target.attr("type") === "number" && element.type === "number") {
                    if (isNaN(Number(value_menor)) || isNaN(Number(value_mayor))) {
                        return false;
                    } else {
                        return Number(value_menor) < Number(value_mayor);
                    }
                } else if (target.attr("type") === "date" && element.type === "date") {
                    var inicio = new Date(value_menor);
                    var fin = new Date(value_mayor);
                    if (Object.prototype.toString.call(inicio) === "[object Date]"
                        && Object.prototype.toString.call(fin) === "[object Date]") {
                        // it is a date
                        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
                            return false;
                        } else {
                            return inicio < fin;
                        }
                    } else {
                        // no es fecha. valido o no? return true o false?
                        return false;
                    }

                } else if (target.attr("type") === "text" && element.type === "text") {
                    return value_menor < value_mayor;
                }
            }
            return true;
        },
        "Por favor, especifique un valor mayor a inicio");

    $.validator.addMethod("mayorIgualA", function (value_mayor, element, param) {
            var target = $(param);
            var value_menor = target.val();
            if (value_mayor !== "" && value_menor !== "") {
                if (target.attr("type") === "number" && element.type === "number") {
                    if (isNaN(Number(value_menor)) || isNaN(Number(value_mayor))) {
                        return false;
                    } else {
                        return Number(value_menor) <= Number(value_mayor);
                    }
                } else if (target.attr("type") === "date" && element.type === "date") {
                    var inicio = new Date(value_menor);
                    var fin = new Date(value_mayor);
                    if (Object.prototype.toString.call(inicio) === "[object Date]"
                        && Object.prototype.toString.call(fin) === "[object Date]") {
                        // it is a date
                        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
                            return false;
                        } else {
                            return inicio <= fin;
                        }
                    } else {
                        // no es fecha. valido o no? return true o false?
                        return false;
                    }

                } else if (target.attr("type") === "text" && element.type === "text") {
                    return value_menor <= value_mayor;
                }
            }
            return true;
        },
        "Por favor, especifique un valor mayor o igual a inicio");

    $.validator.addMethod("menorIgualA", function (value_menor, element, param) {
            var target = $(param);
            var value_mayor = target.val();
            if (value_mayor !== "" && value_menor !== "") {
                if (target.attr("type") === "number" && element.type === "number") {
                    if (isNaN(Number(value_mayor)) || isNaN(Number(value_menor))) {
                        return false;
                    } else {
                        return Number(value_menor) <= Number(value_mayor);
                    }
                } else if (target.attr("type") === "date" && element.type === "date") {
                    var inicio = new Date(value_menor);
                    var fin = new Date(value_mayor);
                    if (Object.prototype.toString.call(inicio) === "[object Date]"
                        && Object.prototype.toString.call(fin) === "[object Date]") {
                        // it is a date
                        if (isNaN(inicio.getTime()) || isNaN(fin.getTime())) {
                            return false;
                        } else {
                            return inicio <= fin;
                        }
                    } else {
                        // no es fecha. valido o no? return true o false?
                        return false;
                    }

                } else if (target.attr("type") === "text" && element.type === "text") {
                    return value_menor <= value_mayor;
                }
            }
            return true;

        },
        "Por favor, especifique un valor menor a fin ");

});