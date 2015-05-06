function [] = fixdatabase(field,value,newvalue)

% FIXDATABASE fix erroneous records in mysql database
%
%       fixdatabase(field,value,newvalue)
%
%  INPUT
%    field    - valid field in exper and dfile (e.g. 'exper')
%    value    - erroneous value (e.g. 'pic0100')
%    newvalue - replacement value (e.g. 'pic0000')
%
%  OUTPUT
%    (status text)
%
%  WARNING: Dangerous Program! Changes Database! 
%           Run program with TEST=1 to determine if all mysql
%           commands are correct, then set TEST=0.
%
% Touryan 07.17.2007

%%% PARAMETERS %%%
TEST = 1;       % Test Mode (1 = print commands, 0 = execute commands)


% -- Initialize MySQL -- %
status = mysql('open', 'alpha', 'root', '');
status = mysql('use mlabdata');



% Get Erroneous Experiments %
eID = mysql(sprintf('select ID from exper where %s="%s"',field,value));
if isempty(eID) 
    warning('No Matching Experiments Found!'); 
end
%%% FIX EXPER %%%
for i = 1:length(eID)
    
    % Get/Display Record Info %
    ID = num2str(eID(i));
    [exper, expdate] = mysql(sprintf('select exper,date from exper where ID="%s"',ID));
    fprintf('Fixing exper: %s in %s \n',exper{:},datestr(expdate,'yyyy-mm-dd'))
    
    % Fix %
    if TEST
        % Print It %
        fprintf('  (')
        fprintf('update exper set %s="%s" where ID="%s"',field,newvalue,ID);
        fprintf(')\n\n')
    else
        % *** Do It *** %
        mysql(sprintf('update exper set %s="%s" where ID="%s"',field,newvalue,ID))
    end
    
end



% Get Erroneous Data Files %
dID = mysql(sprintf('select ID from dfile where %s="%s"',field,value));
if isempty(dID) 
    warning('No Matching Data Files Found!'); 
end
%%% FIX DFILE %%%
for i = 1:length(dID)
    
    % Get/Display Record Info %
    ID = num2str(dID(i));
    [exper, expdate] = mysql(sprintf('select exper,date from dfile where ID="%s"',ID));
    fprintf('Fixing dfile: %s in %s \n',exper{:},datestr(expdate,'yyyy-mm-dd'))
    
    % Fix %
    if TEST
        % Print It %
        fprintf('  (')
        fprintf('update dfile set %s="%s" where ID="%s"',field,newvalue,ID);
        fprintf(')\n\n')
    else
        % *** Do It *** %
        mysql(sprintf('update dfile set %s="%s" where ID="%s"',field,newvalue,ID))
    end
    
    % Fix src %
    if strcmp(field,'exper')
        % Check src for Error %
        src = mysql(sprintf('select src from dfile where ID="%s"',ID));
        src = src{:}; exper = exper{:};
        ind = strfind(src,exper);
        lng = length(exper);
        if ~isempty(ind)
            % Correct src %
            oldsrc = src;
            % Determine Sequence Number (i.e. *.001) %
            src = [src(1:ind-1) newvalue];
            [s,r] = system(sprintf('ls %s.*.[0-9]* | cut -d''.'' -f3 | sort | tail -n1',src));
            if strcmp(r(1:3),'ls:')
                % No Files with New Experiment Prefix: keep sequence %
                src = [src oldsrc(ind+lng:end)];
            else
                % Files with New Experimental Prefix: update sequence %
                seq = num2str(str2num(r) + 1001);
                seq = seq(2:end);
                src = [src oldsrc(ind+lng:end-3) seq];
            end
            if TEST
                % Print It %
                fprintf('  (')
                fprintf('update dfile set src="%s" where ID="%s"',src,ID);
                fprintf(')\n')
                fprintf('  (')
                fprintf('>>mv %s %s',oldsrc,src);
                fprintf(')\n\n')
            else
                % *** Do It *** %
                mysql(sprintf('update dfile set src="%s" where ID="%s"',src,ID))
                system(sprintf('mv %s %s',oldsrc,src));
            end
        end
    end
    
end


% -- Close MySQL -- %
 mysql('close');