(function() {
  var add_condition, remove_condition, remove_operator_arguments, add_operator_arguments, update_conditions_visibility;

  remove_operator_arguments = function(event) {
    console.log('remove_operator_arguments');
    var $operator, $condition_row, name_prefix;

    $operator = $(event.target);
    name_prefix = $operator.attr('id').split('-').slice(0,2).join('-');
    $condition_row = $operator.closest('#' + name_prefix);
    
    return $condition_row.find('input[type=text]').hide();
  };

  add_operator_arguments = function(event) {
    console.log('add operator arguments');
    var $operator, $condition_row, $operators, $arguments, name_prefix, num_new_arguments;

    $operator = $(event.target);
    name_prefix = $operator.attr('name').split('-').slice(0, 2).join('-');
    $condition_row = $operator.closest('#' + name_prefix);

    $arguments = $operator.find('option:selected').data('arguments');

    if (!$arguments) {
        num_new_arguments = 0;
    } else {
        num_new_arguments = $arguments.split(',').length;
    }

    $operators = $condition_row.find('input[type=text]');

    return $operators.each(function(index, operator) {
        if (index < num_new_arguments) {
            $(operator).show();
        }
    });
  };

  add_condition = function(event) {
    var $conditions, $prototype, $num_conditions, $clone;
    console.log('add_condition');
    // Find existing conditions
    $conditions = $(this).parents('ul.switches > li').find('ul.conditions');
    $num_conditions = 'conditions-' + $($conditions).find('li').length;

    // Clone a base condition
    $prototype = $('ul#condition-form-prototype li').first();
    $clone = $prototype.clone(true, true);

    // Prepend condition number to ids and names of clone
    $($clone).attr('id', $num_conditions);
    $($clone).find('*[id]').each(function() { 
        $(this).attr('id', $num_conditions + '-' + $(this).attr('id'));
    });
    $($clone).find('*[name]').each(function() { 
        $(this).attr('name', $num_conditions + '-' + $(this).attr('name'));
    });

    $clone.appendTo($conditions);
    $conditions.find('li').last().find('input,select').removeAttr('selected').attr('value', '');
    $(this).trigger('gutter.switch.conditions.changed');
    return false;
  };

  remove_condition = function(event) {
    console.log('remove_condition');
    var $conditions = $(this).parents('ul.conditions');
    $(this).parents('ul.conditions li').remove();
    $conditions.trigger('gutter.switch.conditions.changed');
    return false;
  };

  update_conditions_visibility = function(event) {
    console.log('update_conditions_visibility');
    var $conditions = $(this).parents('ul.switches li').find('#condition-group');
    switch ($(this).val()) {
      case '1': // disabled
      case '3': // global
        return $conditions.hide();
      case '2': // selective
        return $conditions.show();
    }
  };

  $(function() {
    $('ul.switches > li').delegate('button[data-action=add-condition]', 'click', add_condition);
    $('ul.switches > li').delegate('button[data-action=remove-condition]', 'click', remove_condition);
    $('ul.switches > li').delegate('select[name$=operator]', 'change', remove_operator_arguments);
    $('ul.switches > li').delegate('select[name$=operator]', 'change', add_operator_arguments);
    $('ul.switches > li').delegate('select[name=state]', 'change', update_conditions_visibility);

    $('button[data-action=delete]').click(function() {
      return $(this).parents('form').find('input[name=delete]').attr('value', 'checked');
    });

    $('ul.switches > li select[name=state]').trigger('change');
    $('ul.switches > li select[name$=operator]').trigger('change');
  });

}).call(this);
