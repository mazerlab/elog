function elogatt(dfile, note)
%function elogatt(filename, note)
% attach snapshot of current figure to a datafile in the elog
%
%INPUT
%  dfile - unique string specification of datafile
%  note - text note to insert into log with image
%
%OUTPUT
%  none
%
%NOTES
%  uses elogatt (python) command line attachment tool for
%  heavy lifting
%

if ~exist('dfile', 'var'), dfile=[]; end
if ~exist('note', 'var'), note=[]; end

if isempty(dfile)
  u = get(gcf, 'UserData');
  if isstruct(u) && isfield(u, 'cmd')
    dfile = u.src;
  end
  fprintf('attaching to: %s\n', dfile);
end

tf = [tempname '.jpg'];
if 1
  % this gives a real snapshot.. seems to have less artifacts..
  im = getframe(gcf);
  imwrite(im.cdata, tf, 'Quality', 90);
else
  print('-djpeg', '-r150', tf);
end
[s, w] = unix(sprintf('elogatt %s %s %s', dfile, tf, note));
if s
  error(w)
end
delete(tf);
