function pf = dbfind(pattern, varargin)
%function pf = dbfind(pattern, ...opts...)
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
%    opts -
%       'all' - allow multiple matches
%       'one' -  allow exactly one match
%       'load' - load files (otherwise, just result names)
%       'noload' - load files (otherwise, just result names)
%

%  OUTPUT
%    pf - pypefile datastruct (from p2mLoad2)

%% Parameters
DBHOST = 'sql.mlab.yale.edu';
DBUSER = 'dbusernopass';
DBPASS = '';
DBNAME = 'mlabdata';
BASEDIR = '/auto/data/critters/';

assert(~isempty(pattern), 'pattern required');

multiple_ok = 0;
loadp2m = 1;

if any(strcmp(varargin, 'load')),       loadp2m=1;      end
if any(strcmp(varargin, 'noload')),     loadp2m=0;      end
if any(strcmp(varargin, 'all')),        multiple_ok=1;  end
if any(strcmp(varargin, 'one')),        multiple_ok=0;  end

if ~exist('multiple_ok', 'var')
  multiple_ok = 0;
end

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

if length(src) > 1
  % sort files by run number (last 3 chars) so it's easier to parse
  ns = [];
  for n = 1:length(src)
    ns(n) = str2num(src{n}(end-2:end));
  end
  [~,ix] = sort(ns);
  src = src(ix);
end

if ~multiple_ok
  %Check for a single answer
  if (length(src) > 1)
    for n = 1:length(src)
      fprintf('%s\n', src{n});
    end
    error('multiple expers match "%s"', pattern);
  elseif (isempty(date))
    error('cell %s not found', pattern)
  end
  if loadp2m
    pf = p2mLoad2([src{1} '.p2m']);
  else
    pf = [src{1} '.p2m'];
  end
else
  pf = [];
  for n = 1:length(src)
    if exist(src{n}, 'file')
      if loadp2m
        pf{n} = p2mLoad2([src{n} '.p2m']);
      else
        pf{n} = [src{n} '.p2m'];
      end
    else
      fprintf('warning: %s missing\n', src{n});
    end
  end
end




