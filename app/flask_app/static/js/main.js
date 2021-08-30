$(document).ready(function(){
    $('.tooltipped').tooltip();
});
$(document).ready(function(){
    $('.modal').modal();
});
// Click Add new job
$(function () {
    loadJobs();
    $('#add_icon').click(function (e) {
        $('#add_icon').addClass('hide');
        $('#close_icon').removeClass('hide');
        $('.job_list').addClass('hide');
        $('.add_job').removeClass('hide');
        $('.job_details').addClass('hide');
    })
    $('.nav_logo').click(function(e) {
        $('.toggle_class').addClass('hide');
        $('.job_list').removeClass('hide');
        loadJobs();
    })
    $('#close_icon').click(function (e) {
        $('#close_icon').addClass('hide');
        $('#add_icon').removeClass('hide');
        $('.add_job').addClass('hide');
        $('.job_list').removeClass('hide');
        $('.job_details').addClass('hide');
        loadJobs();
    })
    // Add new job
    $('#start_job_button').click(function (e) {
        e.preventDefault();
        $('.errors').html('');
        var data = $('#add_job_form').serialize();
        $.ajax({
            url: '/api/v1/create_job',
            data: data,
            type: 'POST',
            success: function (response) {
                if (response.status === 'error') {
                    $.each(response.message, function (index, value) {
                        $(index).html(value)
                    })
                } else if (response.status === 'success') {
                    M.toast({html: 'Created Your Job!'})
                    $('#add_job_form').trigger('reset');
                }
            }
        })
    })
});

function loadJobs() {
    // destroy old click events
    $('#job_table_body').off('click', '.delete_class');
    $('#job_table_body').off('click', '.stop_class');
    $('#job_table_body').off('click', '.job_info');
    $('#delete_yes').off('click')
    $('#job_table_body').html('');
    $.ajax({
        url: '/api/v1/get_jobs',
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                $.each(response.data, function(index, value) {
                    stop = '';
                    if (value.status === 'Running') {
                        stop = '<i id="' + value.name + '" class="material-icons stop_class tooltipped" data="' + value.name +'" data-position="bottom" data-tooltip="Stop this job.">stop</i>'
                    }
                    $('#job_table_body').append(
                        '<tr data-name="' + value.name + '"><td>' + value.name + '</td>' +
                        '<td>' + value.status + '</td>' +
                        '<td>' + value.percent_done + ' %</td>' +
                        '<td><i class="material-icons job_info tooltipped" data-name="' + value.name +'" data-position="bottom" data-tooltip="See the details for this job.">info</i>' +
                        stop +
                        '<i class="material-icons delete_class tooltipped" data="' + value.name +'" data-position="bottom" data-tooltip="Delete this job and all the data.">delete</i></td></tr>'
                    )
                })
                $('.tooltipped').tooltip();
            }
        }
    })
    $('#job_table_body').on('click', '.delete_class', function (e) {
        e.preventDefault();
        jobName = e.currentTarget.getAttribute('data');
        $('#delete_header').html('<h4>Delete Job -' + jobName +'</h4>')
        $('#delete_header').data('data', jobName)
        $('.modal').modal('open');

    })
    $('#delete_yes').on('click', function (e) {
        e.preventDefault();
        $('#job_table_body').off('click', '.delete_class');
        jobName = $('#delete_header').data('data');
        token = $('#form_token').attr('data-token');
        data = new FormData();
        data.append( 'csrf_token', token);
        $.ajax({
            url: '/api/v1/delete_job/' + jobName,
            type: 'POST',
            processData: false,
            contentType: false,
            data: data,
            success: function(response) {
                if (response.status === 'success') {
                    M.toast({html: response.message});
                } else if (response.status === 'error') {
                    M.toast({html: response.message})
                };
                loadJobs();
            }
        })
    })
    $('#job_table_body').on('click', '.stop_class', function (e) {
        e.preventDefault();
        jobName = e.currentTarget.getAttribute('data')
        stopId = e.currentTarget.getAttribute('id');
        token = $('#form_token').attr('data-token');
        data = new FormData();
        data.append( 'csrf_token', token);
        $.ajax({
            url: '/api/v1/stop_job/' + jobName,
            type: 'POST',
            processData: false,
            contentType: false,
            data: data,
            success: function(response) {
                M.toast({html: response.message});
                $('#job_table_body').off('click', '.stop_class')
                setTimeout(function() {loadJobs('stop')}, 3500);
            }
        })
    })
    $('#job_table_body').on('click', '.job_info', function (e) {
        // $('.job_details').off('click', '#create_timelapse')
        // Update the nav icon
        $('#add_icon').addClass('hide');
        $('#close_icon').removeClass('hide');
        $('.job_list').addClass('hide')
        $('.add_job').removeClass('hide')

        $('.toggle_class').addClass('hide')
        $('.job_details').removeClass('hide')
        e.preventDefault();
        jobName = e.currentTarget.getAttribute('data-name');
        token = $('#form_token').attr('data-token');
        data = new FormData();
        data.append( 'csrf_token', token);
        $.ajax({
            url: '/api/v1/get_job/' + jobName,
            type: 'GET',
            success: function (response) {
                if (response.status === 'success') {
                    $('#job_details_table').html()
                    var timelapseButton = '<button id="create_timelapse" data-name="'+ response.data.name + '" type="button">Create Timelapse</button>'
                    var tableHtml = '<tr><th>Name</th><td>' + response.data.name + '</td></tr>' +
                        '<tr><th>Status</th><td>' + response.data.status + '</td></tr>' +
                        '<tr><th>Percent Done</th><td>' + response.data.percent_done + ' %</td></tr>' +
                        '<tr><th>Storage Path</th><td>' + response.data.storage_path + '</td></tr>' +
                        '<tr><th>Estimated Size</th><td>' + response.data.estimated_size + ' GB</td></tr>' +
                        '<tr><th>Picture Count</th><td>' + response.data.picture_count + '</td></tr>' +
                        '<tr><th>Resolution</th><td>' + response.data.resolution + '</td></tr>' +
                        '<tr><th>Picture Frequency</th><td>Picture taken every ' + response.data.frequency + ' seconds</td></tr>' +
                        '<tr><th>Job Length</th><td>' + response.data.length + ' minutes</td></tr>'
                    
                    
                    var pictureHtml = '<img id="main_img" data-last-back="' + response.img_pagination.last_back + '" data-base-path="' + 
                        response.img_pagination.base_path + '" class="pictures" src="' + response.img_pagination.latest_picture + '">';
                    var pictureName = response.img_pagination.latest_picture.split('/')
                    pictureName = pictureName[pictureName.length - 1]

                    $('#picture_name').html(pictureName)
                    $('#label_next').attr('data-label', response.img_pagination.last_back)
                    $('#label_back').attr('data-label', response.img_pagination.last_back)
                    $('#label_back').hide();
                    $('#job_details_table').html(tableHtml);
                    $('#picture_section_content').html(pictureHtml);
                    $('#timelapse_button').html(timelapseButton);

                }
            }
        })
    })
    $('.job_details').on('click', '#create_timelapse', function (e) {
        e.preventDefault();
        jobName = e.currentTarget.getAttribute('data-name');
        $.ajax({
            url: '/api/v1/create_timelapse/' + jobName,
            type: 'GET',
            success: function (response) {
                if (response.status === 'success') {
                    M.toast({html: response.message});
                }
            }
        });
    })

}
function nextImg() {
    var next = Math.floor($('#label_next').attr('data-label'));
    $('#label_back').show();
    if (next !== 0) {
        next = next - 1
        if (next === 0) {
            $('#label_next').hide();
        };
        var base_url = $('#main_img').attr('data-base-path');
        var new_url = base_url + next + '.jpg';
        var last_back = $('#main_img').attr('data-last-back');
        $('#main_img').attr('src', new_url);
        $('#label_back').attr('data-label', next);
        $('#label_next').attr('data-label', next);

        var pictureName = new_url.split('/')
        pictureName = pictureName[pictureName.length - 1]

        $('#picture_name').html(pictureName)
    } else if (next === 0) {
        $('#label_next').hide();
    };
}
function backImg() {
    $('#label_next').show();
    var back = Math.floor($('#label_back').attr('data-label'));
    var last_back = Math.floor($('#main_img').attr('data-last-back'));
    if (last_back > back) {
        back = back + 1
        if (last_back <= back) {
            $('#label_back').hide();
        };
        var base_url = $('#main_img').attr('data-base-path');
        var new_url = base_url + back + '.jpg';

        $('#main_img').attr('src', new_url);
        $('#label_back').attr('data-label', back);
        $('#label_next').attr('data-label', back);

        var pictureName = new_url.split('/')
        pictureName = pictureName[pictureName.length - 1]

        $('#picture_name').html(pictureName)
    } else {
        $('#label_back').hide();
    };
}