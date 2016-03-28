%rebase('layout.tpl', title=title)
%#template to display list of projects in an HTML table. Takes a 2D list.
%#Each member of the list is a row in the table. Each member of a row is a cell.
%#Renders the first row as headers.
%#if an item is a tuple with length 2, renders it as an href with the first item as the URL
%#and the second item as the text. 
%#if an item is a tuple with length 4, it renders it as a form input or select:
%#0: input vs select form item
%#1: text vs number (if input) or default value (if select)
%#2: name of form element
%#3: default value in case of input; list of items in case of select
%isaform=False #Is this a form or just a table?
%for row in rows:
  %for col in row:
    %if col and len(col)==4: #Four parameters for an input or select
      %isaform=True #we're filling in a form; flag to create submit button.
    %end #if
  %end #for col
%end #for row

<h1>{{title}}</h1>
%if isaform: #we're filling in a form; create form header
<form action="/updateclub" method="post">
%end #if
<table>
%i=0 #i is 0 for the title row
%for row in rows:
  <tr>
  %for col in row:
    %if i==0:
      %if isinstance(col, (list, tuple)):
    <th><a href="{{col[0]}}">{{col[1]}}</a></th>
      %else:
    <th>{{col}}</th>
      %end #if isinstance(col, (list, tuple))
    %else:
      %if isinstance(col, (list, tuple)):
        %if len(col)==2: #Two parameters for a link
    <td><a href="{{col[0]}}">{{col[1]}}</a></td>
        %elif len(col)==4: #Four parameters for an input or select
          %if col[0]=='input':
    <td><input type="{{col[1]}}" name="{{col[2]}}" value="{{'' if not col[3] else col[3]}}"></td>
          %elif col[0]=='hidden':
    <td><input type="hidden" name="{{col[2]}}" value="{{col[3]}}"></td>
          %elif col[0]=='select':
    <td>
      <select name="{{col[2]}}">
            %for option in col[3]:
              %if option[0]==col[1]:
        <option value="{{option[0]}}" selected="selected">{{option[1]}}</option>
              %else:
        <option value="{{option[0]}}">{{option[1]}}</option>
              %end #if
            %end #for
      </select>
    </td>
          %end #if col[0]
        %end #if len(col)
      %else:
    <td>{{col}}</td>
      %end #if isinstance(col, (list, tuple))
    %end #if i==0
  %end #for col in row
  </tr>
  %i+=1
%end #for row in rows
</table>
%if isaform: #we're filling in a form; create submit button.
<input value="Update club data" type="submit" />
</form>
%end #if
