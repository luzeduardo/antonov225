/*
 * Translated default messages for the jQuery validation plugin.
 * Locale: PT (Portuguese; portuguÃªs)
 * Region: BR (Brazil)
 */
(function ($) {
    $.extend($.validator.messages, {
        required: "Este campo &eacute; obrigat&oacute;rio.",
        remote: "Por favor, corrija este campo.",
        email: "Por favor, forne&ccedil;a um endere&ccedil;o de email v&aacute;lido.",
        url: "Por favor, forne&ccedil;a uma URL v&aacute;lida.",
        date: "Por favor, forne&ccedil;a uma data v&aacute;lida.",
        dateISO: "Por favor, forne&ccedil;a uma data v&aacute;lida (ISO).",
        number: "Por favor, forne&ccedil;a um n&uacute;mero v&aacute;lido.",
        digits: "Por favor, forne&ccedil;a somente d&iacute;gitos.",
        creditcard: "Por favor, forne&ccedil;a um cart&atilde;o de cr&eacute;dito v&aacute;lido.",
        equalTo: "ERRO&#58; A confirmaÃ§Ã£o da senha nÃ£o confere.",
        extension: "Por favor, forne&ccedil;a um valor com uma extens&atilde;o v&aacute;lida.",
        maxlength: $.validator.format("Por favor, forne&ccedil;a n&atilde;o mais que {0} caracteres."),
        minlength: $.validator.format("ERRO&#58; A senha informada deve conter no mÃ­nimo {0} caracteres<br/> com letras minÃºsculas, maiÃºsculas e nÃºmeros. AlÃ©m disso,<br/> nÃ£o deve conter o nome do usuÃ¡rio na senha. "),
        rangelength: $.validator.format("Por favor, forne&ccedil;a um valor entre {0} e {1} caracteres de comprimento."),
        range: $.validator.format("Por favor, forne&ccedil;a um valor entre {0} e {1}."),
        max: $.validator.format("Por favor, forne&ccedil;a um valor menor ou igual a {0}."),
        min: $.validator.format("Por favor, forne&ccedil;a um valor maior ou igual a {0}."),
        nifES: "Por favor, forne&ccedil;a um NIF v&aacute;lido.",
        nieES: "Por favor, forne&ccedil;a um NIE v&aacute;lido.",
        cifEE: "Por favor, forne&ccedil;a um CIF v&aacute;lido."
    });
}(jQuery));