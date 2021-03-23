function pf = dbfind(pattern, varargin)
%function pf = dbfind(pattern, ...opts...)
%
% Query elog database to find cells based on src filename:
%     >> pf = dbfind('pic0254.gratrev.%', 'merge')
%
%INPUT
%  pattern - filename pattern
%     pattern can contain wildcards -- either % to matech
%     anything or a standard regular expression (e.g., .* to
%     matches anything, [0-5] to match numbers 0-5 etc).
%
%  opts -
%     'one'     - require exactly one matching file (default)
%     'merge'   - allow multiple matches and merge into single pf
%     'all'     - allow multiple matches, returns a list of pfs/names
%     'list'    - return list file names instead of loading them
%     'noload'  - same as list..
%     'crapok'  - load crap files (by default is to skip these)
%     'trainok' - allow training files (0000; default is to skip them)
%     'filecheck' - check for missing datafiles
%
%OUTPUT
%    pf - pypefile datastruct (from p2mLoad2 or p2mMerge)

persistent LASTPF

if ~exist('pattern', 'var')
  pf = LASTPF;
  return;
end

%% Parameters

% default sql parameters -- this is potentially confusing, but the
% idea is we try to load settings from sqlconfig.sh (for testing
% in-place), but if that doesn't work, the SQLGLOBALS tag will be
% expanded during by the Makefile during installation

try
  f=fopen('sqlconfig.sh', 'r');
  eval(char(fread(f)'));
  fclose(f);
catch
  %SQLGLOBALS%
end

assert(~isempty(pattern), 'pattern required');

multiple_ok = 0;
loadp2m = 1;
crapok = 0;
trainok = 0;
merge = 0;
filecheck = 0;

if any(strcmp(varargin, 'list')),       multiple_ok=1;loadp2m=0;        end
if any(strcmp(varargin, 'noload')),     loadp2m=0;                      end
if any(strcmp(varargin, 'all')),        multiple_ok=1;                  end
if any(strcmp(varargin, 'one')),        multiple_ok=0;                  end
if any(strcmp(varargin, 'crapok')),     crapok=1;                       end
if any(strcmp(varargin, 'merge')),      multiple_ok=1;merge=1;          end
if any(strcmp(varargin, 'trainok')),    trainok=1;                      end
if any(strcmp(varargin, 'filecheck')),  filecheck=1;                    end

if ~exist('multiple_ok', 'var')
  multiple_ok = 0;
end

if nargout == 0
  load = 0;
end

%% Set up database connection
quiet = mysql('open', HOST, USER, PASS);
status = mysql('use', DB);
if(~status)
  error('mysql error -- status %d', status)
end

%% Query the DB

if crapok
  mod = '';
else
  mod = 'AND NOT crap';
end

if ~trainok
  mod = [mod ' AND not src LIKE "%0000.%" '];
end

if sum(pattern == '%')
  compfn = 'LIKE';
  pattern = ['%' pattern '%'];
else
  compfn = 'REGEXP';
  pattern = ['.*' pattern '.*'];
end
query = sprintf(['SELECT src FROM dfile WHERE src %s "%s" %s' ...
                 ' ORDER BY date, right(src, 3)'], ...
                  compfn, pattern, mod);
[src] = mysql(query);
mysql('close');

if isempty(src)
  error('no match');
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
  k = 1;
  for n = 1:length(src)
    if isempty(src{n})
      keyboard
    end
    if ~isempty(src{n}) && exist(src{n}, 'file')
      if loadp2m
        pf{k} = p2mLoad2([src{n} '.p2m']);
      else
        pf{k} = [src{n} '.p2m'];
      end
      k = k + 1;
    else
      if filecheck || loadp2m
        fprintf('warning: %s missing\n', src{n});
      end
    end
  end
  if merge
    pf = p2mMerge(pf);
  end
end


LASTPF = pf;

