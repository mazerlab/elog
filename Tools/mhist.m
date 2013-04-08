function mhist(back)

if ~exist('back', 'var')
  back = 30;
end

mysql('open', 'alpha', 'root', '');
mysql('use mlabdata');

animals = {'picard', 'flea', 'mercutio'};

for n = 1:length(animals)  
  q = sprintf('SELECT date,weight,water_work+water_sup FROM note WHERE animal="%s" order by date', animals{n});

  [d, wt, h2o] = mysql(q);

  if 1
    subplot(length(animals), 2, 2*n-1);
    set(plot(d, wt, 'ko-'), 'MarkerFaceColor', 'r');
    if back
      xrange(today-back, today);
    end
    yrange(8, 15)
    dateaxis('X', 6);
    title(['wt ' animals{n}]);
    ylabel('kg');
    
    subplot(length(animals), 2, 2*n);
    set(plot(d, h2o, 'ko-'), 'MarkerFaceColor', 'r');
    if back
      xrange(today-back, today);
    end
    yrange(0, 500)
    dateaxis('X', 6);
    title(['h2o ' animals{n}]);
    ylabel('ml');
  end
  
end
xlabel('day');

mysql('close');

