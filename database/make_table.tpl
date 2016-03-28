%rebase('layout.tpl', title=title)
%#template to display list of projects in an HTML table. Takes a 2D list.
%#Each member of the list is a row in the table. Each member of a row is a cell.
%#Renders the first row as headers.
%#if an item is a tuple, renders it as an href with the first item as the URL
%#and the second item as the text. 
<h1>{{title}}</h1>
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
    <td><input type="{{col[1]}}" name="{{col[2]}}" value="{{col[3]}}"</td>
          %elif col[0]=='select':
    <td>
      <select name="{{col[2]}}">
            %for option in col[3]:
        <option value="{{option[0]}}">{{option[1]}}</option>
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
