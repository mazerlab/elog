function pf = dbfind(pattern)
%function pf = dbfind(pattern)
%
% Find datafiles using sql-db -- load if unique, otherwise show
%
% Example:
%
%     >> dbfind pic0254
%     ans = 
%         '/auto/data/critters/picard/2009/2009-06-24/pic0254.flash.000'
%         '/auto/data/critters/picard/2009/2009-06-24/pic0254.flash.001'
%         ...
%         '/auto/data/critters/picard/2009/2009-06-24/pic0254.spotmap.003'
%     >> dbfind pic0254.gratrev
%     ans =
%     /auto/data/critters/picard/2009/2009-06-24/pic0254.gratrev.004
%     >>
%
%  INPUT
%    pattern - filename pattern

%  OUTPUT
%    pf - pypefile datastruct (from p2mLoad2)

%% Parameters
DBHOST = 'sql.mlab.yale.edu';
DBUSER = 'dbusernopass';
DBPASS = '';
DBNAME = 'mlabdata';
BASEDIR = '/auto/data/critters/';

assert(~isempty(pattern), 'pattern required');

if nargout == 0
  load = 0;
end

%% Set up database connection
quiet = mysql('open', DBHOST, DBUSER, DBPASS);
status = mysql('use', DBNAME);
if(~status)
  error('mysql error -- status %d', status)
end

%% Query the DB
pattern = strrep(pattern, '*', '%');
query = sprintf('SELECT src FROM dfile WHERE src LIKE "%%%s%%"', ...
                pattern);
[src] = mysql(query);
mysql('close');

%Check for a single answer
if (length(src) > 1)
  for n = 1:length(src)
    fprintf('%s\n', src{n});
  end
  error('multiple expers match "%s"', pattern)
elseif(isempty(date))
  error('cell %s not found', pattern)
end
pf = p2mLoad2([src{1} '.p2m']);


