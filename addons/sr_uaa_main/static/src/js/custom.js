function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function validateMobile(mobile) {
    const re = /^[0-9]{10}$/;
    return re.test(mobile);
}

function validateName(name) {
    const re = /\d/;
    return re.test(name);
}
function validatePhone(Phone) {
    //    const retPhone = /^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$/;
    const retPhone = /^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{1,4})(?: *x(\d+))?\s*$/;
    return retPhone.test(String(Phone));
}
$(document).ready(function () {


    setTimeout(fade_out, 1000);

    $('input[id=timezone]').val(Intl.DateTimeFormat().resolvedOptions().timeZone);

    //    $('input.uaa_time_picker').datetimepicker();
    function fade_out() {
        $(".form_submit_success").fadeOut().empty();
    }
    $("meet_greet_request_form").submit(function (event) {
        var recaptcha = $("#g-recaptcha-response").val();
        if (recaptcha === "") {
            event.preventDefault();
            document.getElementById('err').innerHTML = "Please verify Captcha";
        } else {
            return true;
        }
    });

    $('#meet_first_page').on('click', function (event) {

        event.preventDefault();
        var $MeetGreetForm = $('#meet_greet_request_form');
        var $airport_name = $MeetGreetForm.find("select[name=airport_name]");
        var $traveler_name = $MeetGreetForm.find("input[name=traveler_name]");
        var $email = $MeetGreetForm.find("input[name=email]");
        var $country_code = $MeetGreetForm.find("select[name=country_code]");
        var $mobile = $MeetGreetForm.find("input[name=mobile]");

        if ((!$airport_name.val()) || (!$traveler_name.val()) || (!$email.val()) || (!$country_code.val()) || (!$mobile.val())) {
            if (!$airport_name.val()) {
                $airport_name.parents('.form-group').next("span.err_msg").remove();
                $airport_name.addClass('is-invalid');
                $("<span class='err_msg' style='color:red;'>Airport Name is Missing!</span>").insertAfter($airport_name.parents('.form-group'));
            }
            else {
                $airport_name.parents('.form-group').next("span.err_msg").remove();
                $airport_name.removeClass('is-invalid');
            }

            if (!$traveler_name.val()) {
                $traveler_name.next("span.err_msg").remove();
                $traveler_name.addClass('is-invalid');
                $("<span class='err_msg' style='color:red;'>Traveller Name is Missing!</span>").insertAfter($traveler_name);
            }
            else {
                if (validateName($traveler_name.val())) {

                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Traveller Name Contains Numbers!</span>").insertAfter($traveler_name);
                }
                else {
                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.removeClass('is-invalid');
                }
            }

            if (!$email.val()) {
                $email.next("span.err_msg").remove();
                $email.addClass('is-invalid');
                $("<span class='err_msg' style='color:red;'>Email Address is Missing!</span>").insertAfter($email);
            }
            else {

                if (!validateEmail($email.val())) {
                    $email.next("span.err_msg").remove();
                    $email.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Please enter a valid Email Address!</span>").insertAfter($email);
                }
                else {
                    $email.next("span.err_msg").remove();
                    $email.removeClass('is-invalid');
                }
            }

            if (!$country_code.val()) {
                if (!$mobile.val()) {
                    $country_code.parents('.form-group').next("span.err_msg").remove();
                    $country_code.addClass('is-invalid');
                    $mobile.addClass('is-invalid');
                    $("<span class='err_msg err_select' style='color:red;'>Country Code and Contact Number is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                }
                else {
                    if (!validatePhone($mobile.val())) {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $mobile.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Country Code  is Missing and Contact Number is invalid!</span>").insertAfter($country_code.parents('.form-group'));
                    }
                    else {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Country Code is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                        $country_code.addClass('is-invalid');
                        $mobile.removeClass('is-invalid');
                    }
                }
            }
            else {
                if (!$mobile.val()) {
                    $country_code.parents('.form-group').next("span.err_msg").remove();
                    $mobile.addClass('is-invalid');
                    $country_code.removeClass('is-invalid');
                    $("<span class='err_msg err_select' style='color:red;'>Contact Number is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                }
                else {
                    if (!validatePhone($mobile.val())) {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $mobile.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Contact Number is invalid!</span>").insertAfter($country_code.parents('.form-group'));
                    }
                    else {
                        $country_code.removeClass('is-invalid');
                        $mobile.removeClass('is-invalid');
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                    }
                }
            }
        }
        else {
            $airport_name.parents('.form-group').next("span.err_msg").remove();
            $traveler_name.next("span.err_msg").remove();
            $country_code.parents('.form-group').next("span.err_msg").remove();
            $email.next("span.err_msg").remove();

            $airport_name.removeClass('is-invalid');
            $traveler_name.removeClass('is-invalid');
            $email.removeClass('is-invalid');
            $country_code.removeClass('is-invalid');
            $mobile.removeClass('is-invalid');
            flag = true
            if ($email.val() && $traveler_name.val()) {
                if (validateName($traveler_name.val())) {
                    flag = false
                    traveler_name.next("span.err_msg").remove();
                    $traveler_name.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Traveller Name Contains Numbers!</span>").insertAfter($traveler_name);

                }
                else {
                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.removeClass('is-invalid');
                }
                if (!validateEmail($email.val())) {
                    flag = false
                    $email.next("span.err_msg").remove();
                    $email.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Please enter a valid Email Address!</span>").insertAfter($email);
                }
                else {
                    $email.next("span.err_msg").remove();
                    $email.removeClass('is-invalid');

                }
                if (flag) {
                    $('#div_meet_first_page').addClass("tab_hide");
                    $('#div_meet_second_page').removeClass("tab_hide");
                }

            }
        }
    });

    $('.wait').on('click', function (event) {
        var self = $(this);
        self.hide();
    });

    $('#transfer_first_page').on('click', function (event) {
        event.preventDefault();
        var $transferGreetForm = $('#airport_transfer_request_form');
        //        var $airport_service_name = $transferGreetForm.find("select[name=service_types]");
        var $airport_service_name = $("#service_types").find(":selected");

        if ($airport_service_name.data('isArrival')) {
            var $pick_airport_name = $transferGreetForm.find("select[name=pick_up_airport_id]");
            var $drop_airport_name = $transferGreetForm.find("input[name=drop_off_location_id]");
        }
        else {
            if ($airport_service_name.data('isDeparture')) {
                var $pick_airport_name = $transferGreetForm.find("input[name=pick_up_location_id]");
                var $drop_airport_name = $transferGreetForm.find("select[name=drop_off_airport_id]");
            }
        }
        var $traveler_name = $transferGreetForm.find("input[name=traveler_name]");
        var $email = $transferGreetForm.find("input[name=email]");
        var $country_code = $transferGreetForm.find("select[name=country_id]");
        var $mobile = $transferGreetForm.find("input[name=contact_number]");
        if ((!$pick_airport_name.val()) || (!$drop_airport_name.val()) || (!$traveler_name.val()) || (!$email.val()) || (!$country_code.val()) || (!$mobile.val())) {
            if (!$pick_airport_name.val()) {
                $pick_airport_name.addClass('is-invalid');
                $pick_airport_name.parents('.form-group').next("span.err_msg").remove();
                $("<span class='err_msg' style='color:red;'>Pickup Location is Missing!</span>").insertAfter($pick_airport_name.parents('.form-group'));
            }
            else {
                $pick_airport_name.removeClass('is-invalid');
                $pick_airport_name.parents('.form-group').next("span.err_msg").remove();
            }

            if (!$drop_airport_name.val()) {
                $drop_airport_name.addClass('is-invalid');
                $drop_airport_name.parents('.form-group').next("span.err_msg").remove();
                $("<span class='err_msg' style='color:red;'>Drop Off Location is Missing!</span>").insertAfter($drop_airport_name.parents('.form-group'));
            }
            else {
                $drop_airport_name.parents('.form-group').next("span.err_msg").remove();
                $drop_airport_name.removeClass('is-invalid');
            }

            if (!$traveler_name.val()) {
                $traveler_name.next("span.err_msg").remove();
                $traveler_name.addClass('is-invalid');
                $("<span class='err_msg' style='color:red;'>Traveller Name is Missing!</span>").insertAfter($traveler_name);
            }
            else {
                if (validateName($traveler_name.val())) {
                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Traveller Name Contains Numbers!</span>").insertAfter($traveler_name);
                }
                else {
                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.removeClass('is-invalid');
                }
            }

            if (!$email.val()) {
                $email.next("span.err_msg").remove();
                $email.addClass('is-invalid');
                $("<span class='err_msg' style='color:red;'>Email Address is Missing!</span>").insertAfter($email);
            }
            else {
                if (!validateEmail($email.val())) {
                    $email.next("span.err_msg").remove();
                    $email.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Please enter a valid Email Address!</span>").insertAfter($email);
                }
                else {
                    $email.next("span.err_msg").remove();
                    $email.removeClass('is-invalid');
                }
            }

            if (!$country_code.val()) {
                if (!$mobile.val()) {
                    $mobile.addClass('is-invalid');
                    $country_code.addClass('is-invalid');
                    $country_code.parents('.form-group').next("span.err_msg").remove();
                    $("<span class='err_msg err_select' style='color:red;'>Country Code and Contact Number is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                }
                else {
                    if (!validatePhone($mobile.val())) {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $mobile.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Country Code  is Missing and Contact Number is invalid!</span>").insertAfter($country_code.parents('.form-group'));
                    }
                    else {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Country Code is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                        $country_code.addClass('is-invalid');
                        $mobile.removeClass('is-invalid');
                    }
                }
            }
            else {
                if (!$mobile.val()) {
                    $mobile.addClass('is-invalid');
                    $country_code.removeClass('is-invalid');
                    $country_code.parents('.form-group').next("span.err_msg").remove();
                    $("<span class='err_msg err_select' style='color:red;'>Contact Number is Missing!</span>").insertAfter($country_code.parents('.form-group'));
                }
                else {
                    if (!validatePhone($mobile.val())) {
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                        $country_code.addClass('is-invalid');
                        $mobile.addClass('is-invalid');
                        $("<span class='err_msg err_select' style='color:red;'>Contact Number is invalid!</span>").insertAfter($country_code.parents('.form-group'));
                    }
                    else {
                        $country_code.removeClass('is-invalid');
                        $mobile.removeClass('is-invalid');
                        $country_code.parents('.form-group').next("span.err_msg").remove();
                    }

                }
            }
        }
        else {
            $pick_airport_name.parents('.form-group').next("span.err_msg").remove();
            $drop_airport_name.parents('.form-group').next("span.err_msg").remove();
            $traveler_name.next("span.err_msg").remove();
            $country_code.parents('.form-group').next("span.err_msg").remove();

            $pick_airport_name.removeClass('is-invalid');
            $drop_airport_name.removeClass('is-invalid');
            $traveler_name.removeClass('is-invalid');
            $country_code.removeClass('is-invalid');
            $mobile.removeClass('is-invalid');
            flag = true
            if ($email.val() && $traveler_name.val()) {
                if (validateName($traveler_name.val())) {
                    flag = false
                    traveler_name.next("span.err_msg").remove();
                    $traveler_name.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Traveller Name Contains Numbers!</span>").insertAfter($traveler_name);

                }
                else {
                    $traveler_name.next("span.err_msg").remove();
                    $traveler_name.removeClass('is-invalid');
                }
                if (!validateEmail($email.val())) {
                    flag = false
                    $email.next("span.err_msg").remove();
                    $email.addClass('is-invalid');
                    $("<span class='err_msg' style='color:red;'>Please enter a valid Email Address!</span>").insertAfter($email);
                }
                else {
                    $email.next("span.err_msg").remove();
                    $email.removeClass('is-invalid');
                }
                if (flag) {
                    $('#div_transfer_first_page').addClass("tab_hide");
                    $('#div_transfer_second_page').removeClass("tab_hide");
                }
            }


        }
    });

    $('#meet_second_page').on('click', function (event) {
        event.preventDefault();
        $('#div_meet_first_page').removeClass("tab_hide");
        $('#div_meet_second_page').addClass("tab_hide");
    });
    $('#transfer_second_page').on('click', function (event) {
        event.preventDefault();
        $('#div_transfer_first_page').removeClass("tab_hide");
        $('#div_transfer_second_page').addClass("tab_hide");
    });
    $('#service_types').on('change', function (event) {
        event.preventDefault();
        var self = $(this).parent();
        var $x = $("#service_types").find(":selected");
        if ($x.data('isDeparture')) {

            $('#departure_date_div').removeClass("tab_hide");
            $('#arrival_date_div').addClass("tab_hide");
            $('#departure_time_div').removeClass("tab_hide");
            $('#arrival_time_div').addClass("tab_hide");
            $('#departure_flight_div').removeClass("tab_hide");
            $('#arrival_flight_div').addClass("tab_hide");

            $('#departure_airport_div').removeClass("tab_hide");
            $('#departure_location_div').addClass("tab_hide");
            $('#arrival_airport_div').addClass("tab_hide");
            $('#arrival_location_div').removeClass("tab_hide");

        }
        if ($x.data('isArrival')) {
            $('#departure_date_div').addClass("tab_hide");
            $('#arrival_date_div').removeClass("tab_hide");
            $('#departure_time_div').addClass("tab_hide");
            $('#arrival_time_div').removeClass("tab_hide");
            $('#departure_flight_div').addClass("tab_hide");
            $('#arrival_flight_div').removeClass("tab_hide");

            $('#departure_airport_div').addClass("tab_hide");
            $('#departure_location_div').removeClass("tab_hide");
            $('#arrival_airport_div').removeClass("tab_hide");
            $('#arrival_location_div').addClass("tab_hide");

        }
        if ($x.data('isTransit')) {
            $('#departure_date_div').removeClass("tab_hide");
            $('#arrival_date_div').removeClass("tab_hide");
            $('#departure_time_div').removeClass("tab_hide");
            $('#arrival_time_div').removeClass("tab_hide");
            $('#departure_flight_div').removeClass("tab_hide");
            $('#arrival_flight_div').removeClass("tab_hide");
        }

    });


    //Initialize Select2 Elements
    $('.select2').select2()

    //Initialize Select2 Elements
    $('.select2bs4').select2({
        theme: 'bootstrap4'
    })
    $('select[name=country_id]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-countries',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });
    $('select[id=country_code]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-countries',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });
    $('select[name=airport_id]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-airports',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });
    $('select[id=airport_id]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-airports',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });
    $('select[name=pick_up_airport_id]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-airports',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });
    $('select[name=drop_off_airport_id]').select2({
        selectOnClose: true,
        ajax: {
            url: '/api/website/get-all-airports',
            dataType: 'json',
            processResults: function (data) {
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            text: item.name,
                            id: item.id
                        }
                    })
                };
            }
        }
    });

});
