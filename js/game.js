/*
 * 0 - Empty
 * 1 - One Pass
 * 2 - Two Pass
 * 3 - Three Pass
 * 4 - Disabled
 * 5 - Power Up
 * 6 - Health
 * 9 - Door
 */ 


var playfield_width  = 25;
var playfield_height = 25;
var enemy_speed = 1000;
var health = 6;
var max_health = 4;
var score = 0;

var enemy_sprite       = 'enemy';
var player_sprite      = 'player';
var hurt_sprite        = 'hurt';
var goal_open_sprite   = 'door-open';
var goal_closed_sprite = 'door-closed';
var life_sprite        = 'heart';
var life_add_sprite    = 'heart-gift';
var powerup_sprite     = 'star';

var started = false;
var paused  = false;
var player = Array(0, 0);
var player_facing = null;
var enemy  = Array(playfield_width-1, playfield_height-1);
var goal_needed = Math.floor(playfield_width * playfield_height * .25) // 25% of total cells
var goal_completed = 0;

var playfield = createArray(playfield_width, playfield_height);

function placeSpecials() {

    for (i = 0; i <= 5; i++) {
        var type = 5;
        if (i == 4) type = 6;
        if (i == 5) type = 9;

        do {
            x = rand(1, playfield_width-1);
            y = rand(1, playfield_height-1);
        }
        while (playfield[x][y] != 0);

        playfield[x][y] = type;

        if (i == 5) console.log('Goal at ('+ x +','+ y +')');
    }
}


function rand(min, max) {
   var range = (max - min) + 1;
   return Math.floor(Math.random() * range) + min;
}

function createArray(length) {
    // https://stackoverflow.com/questions/966225/how-can-i-create-a-two-dimensional-array-in-javascript/966938#966938
    var arr = new Array(length || 0),
        i = length;

    if (arguments.length > 1) {
        var args = Array.prototype.slice.call(arguments, 1);
        while(i--) arr[length-1 - i] = createArray.apply(this, args);
    }

    return arr;
}

function changeHealth(amount = 0) {
    health += amount;

    if (health > max_health) health = max_health;
    else if (health > 1)     $("#playwindow").removeClass('danger');
    else if (health == 1)    $("#playwindow").addClass('danger');


    var html = '';
    for (i = 0; i < health; i++) {
        html += '<span class="em sprite em-' + life_sprite + '"></span>';
    }
    $(".hearts").html(html);
}

function changeScore(amount = 0) {
    score += amount;

    $('.score').html(score);
}

function playerHurt() {
    var pos = Array(player[0], player[1]);
    
    $('#cell-' + pos[0] + '-' + pos[1]).removeClass('em-' + player_sprite);
    $('#cell-' + pos[0] + '-' + pos[1]).addClass('em-' + hurt_sprite);

    setTimeout(function() {
        $('#cell-' + pos[0] + '-' + pos[1]).removeClass('em-' + hurt_sprite);

        if (pos[0] == player[0] && pos[1] == player[1]) {
            $('#cell-' + pos[0] + '-' + pos[1]).addClass('em-' + player_sprite);
        }
    }, 500);

    changeHealth(-1);
}

function moveEnemy() {
    if (paused == true || started == false) return;

    var old_x = enemy[0];
    var old_y = enemy[1];
    var new_x = old_x;
    var new_y = old_y;

    if (player[0] > old_x) new_x++;
    if (player[0] < old_x) new_x--;
    if (player[1] > old_y) new_y++;
    if (player[1] < old_y) new_y--;

    if (new_x == player[0] && new_y == player[1]) {
        console.log('Enemy: attacks!');

        playerHurt(player[0], player[1]);
    }
    else if (new_x != old_x || new_y != old_y) {

        // hide special sprites temporarily if the enemy is in the same cell
        if (playfield[new_x][new_y] > 10) {
            $('#cell-'+ new_x +'-'+ new_y).removeClass('em-' + goal_sprite + ' em-' + powerup_sprite + ' em-' + life_add_sprite);
        }

        // restore hidden special sprites
        switch (playfield[old_x][old_y]) {
            case 50:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + powerup_sprite);
                break;
            case 60:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + life_add_sprite);
                break;
            case 90:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + goal_closed_sprite);
                break;
        }

        $('.em-' + enemy_sprite).removeClass('em-' + enemy_sprite);
        enemy = Array(new_x, new_y);
        $('#cell-' + new_x + '-' + new_y).addClass('em-' + enemy_sprite);
    }
}

function move(action) {
    if (paused == true || started == false) return;

    var old_x = player[0];
    var old_y = player[1];
    var new_x = old_x;
    var new_y = old_y;

    var blocked = false;

    if (action == 'jump') {
        direction = player_facing;
        spaces = 2;
    }
    else {
        direction = action;
        player_facing = direction;
        spaces = 1;
    }

    switch (direction) {
        case 'up':
            new_y -= spaces;
            break;
        case 'down':
            new_y += spaces;
            break;
        case 'left':
            new_x -= spaces;
            break;
        case 'right':
            new_x += spaces;
            break;
    }

    if ((new_x < 0) || (new_x > playfield_width - 1) || (new_y < 0) || (new_y > playfield_height - 1))  blocked = true; // out of bounds
    else if (new_x == enemy[0] && new_y == enemy[1]) blocked = true; // enemy in cell
    else if (playfield[new_x][new_y] == 4) blocked = true; // cell disabled
    else if (playfield[new_x][new_y] == 90) { // goal has been discovered
        if (goal_needed < goal_completed) { // not enough cells disabled
            blocked = true;
        }
        else {
            // TODO: win!
        }
    }
    else { // valid move

        $('.em-' + player_sprite).removeClass('em-' + player_sprite);
        $('#cell-' + new_x + '-' + new_y).addClass('em-' + player_sprite);
        player = Array(new_x, new_y);


        switch (playfield[old_x][old_y]) {
            case 50:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + powerup_sprite);
                break;
            case 60:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + life_add_sprite);
                break;
            case 90:
                $('#cell-' + old_x + '-' + old_y).addClass('firstpass em-' + goal_closed_sprite);
                break;
        }

        switch (playfield[new_x][new_y]){
            case 0:
                playfield[new_x][new_y]++;
                $('#cell-' + new_x + '-' + new_y).removeClass('empty').addClass('firstpass');
                break;
            case 1:
                playfield[new_x][new_y]++;
                $('#cell-' + new_x + '-' + new_y).removeClass('firstpass').addClass('secondpass');
                break;
            case 2:
                playfield[new_x][new_y]++;
                $('#cell-' + new_x + '-' + new_y).removeClass('secondpass').addClass('thirdpass');
                break;
            case 3:
                playfield[new_x][new_y]++;
                $('#cell-' + new_x + '-' + new_y).removeClass('thirdpass').addClass('disabled');

                goal_completed++;
                if (goal_completed >= goal_needed) {
                    $('.em-' + goal_closed_sprite).addClass('em-' + goal_open_sprite).removeClass('em-' + goal_closed_sprite);
                }

                changeScore(1);
                break;
            case 5:
                playfield[new_x][new_y] = 50;
                break;
            case 6:
                playfield[new_x][new_y] = 60;
                break;
            case 9:
                playfield[new_x][new_y] = 90;
                break;
            case 50:
                playfield[new_x][new_y] = 2;
                $('#cell-' + new_x + '-' + new_y).removeClass('firstpass em-' + powerup_sprite).addClass('secondpass');
                changeScore(10);
                break;
            case 60:
                playfield[new_x][new_y] = 2;
                $('#cell-' + new_x + '-' + new_y).removeClass('firstpass em-' + life_add_sprite).addClass('secondpass');
                changeScore(25);
                changeHealth(1);
                break;
        }

        console.log('Player: (' + new_x + ', ' + new_y + ') facing ' + player_facing);
    }

    if (blocked == true) {
        console.log('Player: ' + (action == 'jump' ? "jump " + direction : "move " + direction) + ' blocked');
    }
}



$(function() {

    if (started == false) {
        $('#start-game').show();
        $('#playfield').addClass('overlay');

        for (var y = 0; y < playfield_height; y++) {
            $("#playfield").append("<div class='game-row'>");
            for (var x = 0; x < playfield_width; x++) {
                playfield[x][y] = 0;
                $("#playfield").append("<span id='cell-"+ x +"-"+ y +"' class='cell empty em' title='[" + x + "," + y + "]'></span>");
            }
            $("#playfield").append("</div>");
        }

        playfield[0][0] = 1;
        $("#cell-" + player[0] + "-" + player[1]).addClass('firstpass em-' + player_sprite);
        $("#cell-" + enemy[0] + "-" + enemy[1]).addClass('em-' + enemy_sprite);

        placeSpecials();
        changeHealth();
        changeScore();
    }



    $(window).keydown(function(e) {
        var key = e.keyCode || e.which;

        switch (key) {
            case 87: // w
            case 38: // up arrow
                move('up');
                break;
            case 83: // s
            case 40: // down arrow
                move('down');
                break;
            case 68: // d
            case 39: // right arrow
                move('right');
                break;
            case 65: // a
            case 37: // left arrow
                move('left');
                break;
            case 32: // space
                move('jump');
                break;
            case 80: // p
                if (started == true) {
                    if (paused == false) {
                        paused = true;
                        $('#playfield').addClass('overlay');
                        $('#paused').show();
                    }
                    else {
                        paused = false;
                        $('#playfield').removeClass('overlay');
                        $('#paused').hide();
                    }
                }
                break;
            case 13: // enter
                if (started == false) {
                    started = true;
                    $('#start-game').hide();
                    $('#playfield').removeClass('overlay');
                }
                break;
            default:
                console.log('Unsupported Key: ' + key);
        }
        e.preventDefault();
    });

    window.setInterval(moveEnemy, enemy_speed);
}); 
