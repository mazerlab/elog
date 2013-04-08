mysql('open', 'alpha', 'root', '');
mysql('use mlabdata');

animals = {'picard', 'flea', 'mercutio'};

[d] = mysql('select date from note where 1 order by date');
d0 = min(d);
dmax = max(d)-d0;
  

for n = 1:length(animals)
  subplot(length(animals), 1, n);
  
  [d, wt, h2o] = mysql(sprintf('select date,weight,water_work+water_sup from note where animal="%s" order by date', animals{n}));
  d = d - d0;

  [ax, h1, h2] = plotyy(d, wt, d, h2o);
  set(get(ax(1), 'ylabel'), 'string', 'weight (kg)');
  set(get(ax(2), 'ylabel'), 'string', 'water (ml)');
  set(ax(1), 'xlim', [0, dmax]);
  set(ax(2), 'xlim', [0, dmax]);
  set(h1, 'marker', 'o');
  set(h2, 'marker', 'o');
  title(animals{n});
end
xlabel('day');

mysql('close');

