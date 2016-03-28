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
    <td><a href="{{col[0]}}">{{col[1]}}</a></td>
      %else:
    <td>{{col}}</td>
      %end #if isinstance(col, (list, tuple))
    %end #if i==0
  %end #for col in row
  </tr>
  %i+=1
%end #for row in rows
</table>
