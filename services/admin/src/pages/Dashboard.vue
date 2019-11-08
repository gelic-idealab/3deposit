<template>
  <div>

    <!--Stats cards-->
    <div class="row">
      <div class="col-md-6 col-xl-2" v-for="stats in statsCards" :key="stats.title">
        <stats-card>
          <div class="icon-big text-center" :class="`icon-${stats.type}`" slot="header">
            <i :class="stats.icon"></i>
          </div>
          <div class="numbers" slot="content">
            <p>{{stats.title}}</p>
            {{stats.value}}
          </div>
          <div class="stats" slot="footer">
            <i :class="stats.footerIcon"></i> {{stats.footerText}}
          </div>
        </stats-card>
      </div>
    </div>

    <!--Charts-->
    <div class="row">

      <div class="col-12">
        <chart-card title="Users behavior"
                    sub-title="24 Hours performance"
                    :chart-data="usersChart.data"
                    :chart-options="usersChart.options">
          <span slot="footer">
            <i class="ti-reload"></i> Updated 3 minutes ago
          </span>
          <div slot="legend">
            <i class="fa fa-circle text-info"></i> Open
            <i class="fa fa-circle text-danger"></i> Click
            <i class="fa fa-circle text-warning"></i> Click Second Time
          </div>
        </chart-card>
      </div>

      <div class="col-md-6 col-12">
        <chart-card title="Deposits"
                    sub-title="Distribution by Media Type"
                    :chart-data="preferencesChart.data"
                    chart-type="Pie">
          <span slot="footer" >
            <i class="ti-timer"></i> Updated now</span>
          <div slot="legend" v-for="(label, index) in preferencesChart.data.labels" :key="label">
            <i class="fa fa-circle" :class="`text-${preferencesChart.data.colors[index]}`"></i> {{label}}
          </div>
        </chart-card>
      </div>

      <div class="col-md-6 col-12">
        <chart-card title="2015 Sales"
                    sub-title="All products including Taxes"
                    :chart-data="activityChart.data"
                    :chart-options="activityChart.options">
          <span slot="footer">
            <i class="ti-check"></i> Data information certified
          </span>
          <div slot="legend">
            <i class="fa fa-circle text-info"></i> Tesla Model S
            <i class="fa fa-circle text-warning"></i> BMW 5 Series
          </div>
        </chart-card>
      </div>

    </div>

  </div>
</template>
<script>
import { StatsCard, ChartCard } from "@/components/index";
import Chartist from 'chartist';
import axios from 'axios';

export default {
  components: {
    StatsCard,
    ChartCard
  },
  methods: {
    convertSize(value) {
      if (value <= 1.0e+6) {
        return Math.round((value/1.0e+3)).toString() + 'KB'
      }
      if (value > 1.0e+6 && value <= 1.0e+9) {
        return Math.round((value/1.0e+6)).toString() + 'MB'
      }
      if (value > 1.0e+9) {
        return Math.round((value/1.0e+9)).toString() + 'GB'
      }
    },
    fetchCountByMediaTypes(list_of_deposits) {
      var media_types = new Map()
      for(var i=0; i<list_of_deposits.length; i++) {
        var mt = list_of_deposits[i]['deposit_metadata']['media_type']
        if(media_types.has(mt)){
          media_types.set(mt, media_types.get(mt)+1)
        } else {
          media_types.set(mt,1)
        }
      }
      console.log(media_types)
      var color = ['#EF5350', '#00BCD4', '#FFC107']
      var counter = 0;
      var keys = [];
      var values = [];
      for(const [key, value] of media_types.entries()) {
        keys.push(key);
        values.push(value);
      }
      return [keys, values]
    }

  },
  /**
   * Chart data used to render stats, charts. Should be replaced with server data
   */
  data() {
    return {
       statsCards: [
        {
          type: "warning",
          icon: "ti-server",
          title: "Used Size",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        },
        {
          type: "success",
          icon: "ti-wallet",
          title: "Deposits",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        },
        {
          type: "danger",
          icon: "ti-pulse",
          title: "Largest File",
          value: '',
          footerText: "Updated now",
          footerIcon: "ti-reload"
        }
        // {
        //   type: "info",
        //   icon: "ti-twitter-alt",
        //   title: "Followers",
        //   value: "+45",
        //   footerText: "Updated now",
        //   footerIcon: "ti-reload"
        // }
      ],
      usersChart: {
        data: {
          // labels: [
          //   "9:00AM",
          //   "12:00AM",
          //   "3:00PM",
          //   "6:00PM",
          //   "9:00PM",
          //   "12:00PM",
          //   "3:00AM",
          //   "6:00AM"
          // ],
          // series: [
          //   [287, 385, 490, 562, 594, 626, 698, 895, 952],
          //   [67, 152, 193, 240, 387, 435, 535, 642, 744],
          //   [23, 113, 67, 108, 190, 239, 307, 410, 410]
          // ]
        },
        options: {
          low: 0,
          high: 1000,
          showArea: true,
          height: "245px",
          axisX: {
            showGrid: false
          },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: true,
          showPoint: false
        }
      },
      activityChart: {
        data: {
          labels: [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "Mai",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
          ],
          series: [
            [542, 543, 520, 680, 653, 753, 326, 434, 568, 610, 756, 895],
            [230, 293, 380, 480, 503, 553, 600, 664, 698, 710, 736, 795]
          ]
        },
        options: {
          seriesBarDistance: 10,
          axisX: {
            showGrid: false
          },
          height: "245px"
        }
      },
      preferencesChart: {
        data: {
          labels: [],
          series: [],
          colors: []
        },
        // {
        //   labels:
        //   value:
        //   color:
        // }
        // labels: ["62%", "32%", "6%"],
        //  series: [62, 32, 6]

        options: {}
      },
      mongo_data: {}
    };
  },
  mounted() {
    axios.get('../api/store/buckets', {params: {'bucket_name': '3deposit'}})
    .then(response => {
      this.statsCards[0].value = this.convertSize(response.data.bucket_size);
      this.statsCards[1].value = response.data.num_files;
      this.statsCards[2].value = this.convertSize(response.data.largest_file);
    });
    axios.get('../api/mongo')
    .then(response => {
      console.log(this)
      this.mongo_data = response.data.stats
      var result_list = this.fetchCountByMediaTypes(response.data.stats)
      this.preferencesChart.data.labels = result_list[0]
      this.preferencesChart.data.series = result_list[1]
      this.preferencesChart.data.colors = ['info', 'warning', 'danger']
    });
  }
};
</script>
<style>
</style>
