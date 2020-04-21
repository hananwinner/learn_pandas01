ver=$1
eval /usr/bin/rcv.sh mymovie/api/template.yaml $ver
eval /usr/bin/rcv.sh mymovie/aggregator/agg_cf.yaml $ver
