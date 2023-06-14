<template>
    <div class="search">
        <a-input-search placeholder="input search text" enter-button @search="onSearch" style="width: 80%; margin-top: 20px;"/>
        <a-row style="margin-top: 20px; font-size: 150%; margin-left: -175px;">Total {{ totalResult }} Results found. {{ latency }} second.</a-row>
        <a-row type="flex" justify="center">
            <a-col :span="8">
                <a-collapse v-model="activeKey1" style="width: 90%; margin-top: 20px; font-size: 125%;">
                    <a-collapse-panel :key="index.toString()" :header="'Summarization ' + (index + 1).toString()" v-for="(item, index) in summary" >
                        <div style="text-align: start;">
                            {{ item.text }}
                            <div v-for="(relatedUrl, id) in item.related" :key="id">
                                <a style="color: rgb(45, 183, 245);" :href="relatedUrl">
                                    {{id + 1}}. {{ relatedUrl }}
                                </a>
                            </div>
                        </div>
                    </a-collapse-panel>
                </a-collapse>
            </a-col>
            <a-col :span="8">
                <a-collapse v-model="activeKey2" style="width: 80%; margin-top: 20px; font-size: 125%;">
                    <a-collapse-panel key="1" header="Q&A">
                        <div style="text-align: start;">
                            {{ qa.answer }}
                            <div v-for="(relatedUrl, id) in qa.related" :key="id">
                                <a style="color: rgb(45, 183, 245);" :href="relatedUrl">
                                    {{id + 1}}. {{ relatedUrl }}
                                </a>
                            </div>
                        </div>
                    </a-collapse-panel>
                </a-collapse>
            </a-col>
        </a-row>
        <a-row type="flex" justify="center">
        <a-list
            class="demo-loadmore-list"
            :loading="loading"
            item-layout="horizontal"
            :data-source="resultShown"
            style="width: 80%; margin-top: 20px;"
        >
            <div
                v-if="showLoadingMore"
                slot="loadMore"
                :style="{marginTop: '12px', height: '32px', lineHeight: '32px' }"
            >
            <a-spin v-if="loadingMore" />
            <a-button v-else @click="onLoadMore">
                loading more
            </a-button>
            </div>
            <a-list-item slot="renderItem" slot-scope="item, index">
                <a-list-item-meta
                >
                    <a-row slot="title" style="font-size: 125%;" type="flex" justify="start">
                        <a-col :span="9.5" style="text-align: start;">
                            <a-tag color="blue" style="font-size: 100%;">
                                <a :href="item.url" style="color: rgb(45, 183, 245);">{{ item.url }}</a>
                            </a-tag>
                        </a-col>
                        <a-col :span="7" style="text-align: start; margin-right: 30px;">
                            <a-tag color="cyan" style="font-size: 100%">{{ item.timestamp }}</a-tag>
                        </a-col>
                    </a-row>
                    <!-- <a slot="title" :href="item.url" style="font-size: 125%;">{{ item.url }}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ item.timestamp }}</a> -->
                    <a-button size="large" slot="avatar" style="margin-top: 5px;">
                        {{ index+1 }}
                    </a-button>
                    <div slot="description" style="text-align: start;">{{ item.text.substr(0, 720) + '...' }}</div>
                </a-list-item-meta>
                <div style="width: 200px;">
                    <a-button type="primary" @click="showDrawer(index)">
                        Detail
                    </a-button>
                    <a-drawer
                        title="News Detail"
                        placement="right"
                        :closable="true"
                        :visible="drawerVisible"
                        @close="closeDrawer"
                        width="800"
                        >
                            <p>{{ drawerText }}</p>
                    </a-drawer>
                </div>
            <!-- <div>{{ item.text }}</div> -->
            </a-list-item>
        </a-list>
    </a-row>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data(){
        return {
            loading: true,
            loadingMore: false,
            showLoadingMore: true,
            drawerVisible: false,
            drawerText: '',
            totalResults: 0,
            activeKey1: [],
            activeKey2: [],
            result: [],
            resultShown: [],
            totalResult: 0,
            pageSize: 5,
            summary: [],
            qa: {},
            latency: 0,
        }
    },
    mounted() {
        this.loading = false;
    },
    name: 'Search',
    methods: {
        onSearch(value) {
            if (value.includes('Boolean ')) this.getData("Boolean", value.substr(8, value.length - 8))
            else this.getData("Ranked", value)
        },
        getData(type, query) {
            var input = {'type': type, 'query': query}
            console.log('input', input)
            axios.post('http://127.0.0.1:5000/search', input).then(res => {
                console.log(res)
                this.result = res.data.result
                this.latency = res.data.time
                this.totalResult = res.data.cnt
                if (typeof(res.data.summary) == 'undefined') {
                    this.summary = []
                } else {
                    this.summary = res.data.summary
                }
                if (typeof(res.data.qa) == 'undefined') {
                    this.qa = {}
                } else {
                    this.qa = res.data.qa
                }
                this.resultShown = []
                this.onLoadMore()
            })
            // var res = {
            //     "code": 200,
            //     "msg": "OK",
            //     "result": [
            //         {
            //             "text": "Cluster comprises IBM's Opteron-based eServer 325 server and systems management software and storage devices that can run Linux and Windows operating systems.\nIBM on Tuesday announced a prepackaged and pretested cluster that is powered by Advanced Micro Devices Inc.s 64-bit Opteron processor.\nIBM, of Armonk, N.Y., is combining its Opteron-based eServer 325 server—which targets scientific and technical computing users—with systems management software and storage devices to offer a bundled package that can run Linux and Windows operating systems.\nThe new offering, which will be available later this month or in early December, is part of IBMs eServer Cluster 1350, which also includes bundles based on the companys BladeCenter blade servers and two-processor x335 and x345 systems using Intel Corp.s 32-bit Xeon chips.\nClusters comprise multiple servers tied together to create a supercomputing environment for users. In a related move, IBM last week announced that it was teaming with Corning Inc., the U.S. Department of Energy and the National Nuclear Security Administration to develop high-speed, optically switched interconnects for supercomputers. The $20 million, two-and-a-half-year project is aimed at increasing network bandwidth by 50 times while at the same time cutting the costs of supercomputers.\nIBMs 325 systems, powered by 2GHz Opterons, give users a chance to run both their 32-bit and 64-bit applications on a single platform, which is important for mixed-use environments, said David Turek, vice president of IBMs Deep Computing unit.\n\"For many of these users, who have been left with a stark choice—you either run 32-bit or 64-bit—Opteron is an interesting bridge between the two,\" Turek said. \"Its an attractive proposition.\"\nAMD, of Sunnyvale, Calif., has pushed Opterons ability to run 32-bit applications as well as it does 64-bit applications as a key differentiator between it and Intels Itanium architecture. The 64-bit Itanium chip maintains a limited amount of backward compatibility, which means that it does not run the 32-bit applications as well as it does the 64-bit software.\nWith the latest Itanium 2 released this summer, officials with Intel, of Santa Clara, Calif., were promoting the companys IA-32 Execution Layer, designed to bridge that performance gap. Intel, which has pushed Xeon-based systems for 32-bit applications and Itanium for 64-bit computing, views the execution layer as a way of helping customers who want to move to 64-bit computing but still have older 32-bit applications running.\nOn Monday, Intel officials said that a software update from Microsoft Corp. that includes the execution layer for Windows applications has been delayed until the second half of next year. However, they said that Linux vendors, including Red Hat Inc. and SuSE Linux AG, both are incorporating the execution layer code in their offerings.\n/zimages/3/28571.gifRead \"MS Delay Hinders Itanium Software Upgrade.\"\nGordon Haff, an analyst with Illuminata Inc., said Opterons adoption path is mirroring that of the older Itanium technology.\n\"Theres a lot of interest in Opteron in [the high-performance computing space]; its nearly exclusively in HPC,\" said Haff, in Nashua, N.H. \"Its a good performing chip, and thats pretty much what HPC [customers are] looking for.\"\nWhile backward compatibility with 32-bit applications may make Opteron more attractive in the commercial space, HPC users are more interested in performance, he said.\nTurek agreed. \"The Intel name carries a lot of weight in the industry,\" he said. That said, HPC and technical computing customers tend to be among the early adopters of new technology.\n\"Theyre searching for the best technology without so much regard for the brand,\" he said.\nThe Opteron cluster offering includes IBM Cluster Management Software, which aims to avoid problems and speed up the resolution of problems that do occur by automating repetitive tasks and error detection.\nAlso included in the cluster package is a new Linux Cluster Install Tool, which automates much of the installation work, IBM officials said.\nIn the supercomputing interconnect project, Cornings Science & Technology Division, in Corning, N.Y., will create a prototype for an optically switched interconnect. IBM Research Labs in the United States and Switzerland will build the systems electronic control and monitoring circuitry.",
            //             "timestamp": "2019-04-19T18:35:24Z",
            //             "url": "https://www.eweek.com/networking/ibm-takes-wraps-off-opteron-based-cluster"
            //         },
            //         {
            //             "text":"Belying expectations, Prasar Bharti has earned only Rs 58.19 crore (Rs 581.9 million) as revenue during the Commonwealth Games last month.\nThe gross revenue earned by PB on account of telecasting/broadcasting of advertisements on Doordarshan channel and All India Radio during coverage of the Commonwealth Games is Rs 58.17 crore, Minister of State for Information and Broadcasting S Jagathrakshakan informed the Lok Sabha on Tuesday.\nWhile AIR earned Rs 2.18 crore (Rs 21.8 million), Doordarshan garnered Rs 55.99 crore (Rs 559.9 million) as revenue, he said. Prasar Bharati had earlier said it knew in advance that the recently concluded Commonwealth Games, for which Doordarshan was the official broadcaster, would not bring in huge advertising revenues.\nas a result of luke warm response from advertisers.\nNotably, DD was not allowed to air advertisements during the closing ceremony of the CWG Games following complaints that the opening ceremony had been shown deferred live to accommodate advertisements.\nAfter a successful opening ceremony, DD had hiked ad spot rates for the closing ceremony to Rs 2.5 lakh for a ten second spot as compared with Rs 90,000 for the same in the opening of the CWG.",
            //             "timestamp":"2019-04-20T00:13:19Z",
            //             "url":"https://www.rediff.com/money/report/cwg-prasar-bharti-earns/20101109.htm"
            //         },
            //         {
            //             "text":"text C",
            //             "timestamp":"timestamp C",
            //             "url":"url C"
            //         },
            //         {
            //             "text":"text D",
            //             "timestamp":"timestamp D",
            //             "url":"url D"
            //         }
            //     ],
            //     "summary": [
            //         {
            //             "text": "summary A",
            //             "related": ["https://www.eweek.com/networking/ibm-takes-wraps-off-opteron-based-cluster", "https://www.rediff.com/money/report/cwg-prasar-bharti-earns/20101109.htm"]
            //         },
            //         {
            //             "text": "summary B",
            //             "related": ["https://www.eweek.com/networking/ibm-takes-wraps-off-opteron-based-cluster", "https://www.rediff.com/money/report/cwg-prasar-bharti-earns/20101109.htm"]
            //         },
            //         {
            //             "text": "summary C",
            //             "related": ["https://www.eweek.com/networking/ibm-takes-wraps-off-opteron-based-cluster", "https://www.rediff.com/money/report/cwg-prasar-bharti-earns/20101109.htm"]
            //         }
            //     ],
            //     "qa": {
            //         "answer": "answer A",
            //         "related": ["https://www.eweek.com/networking/ibm-takes-wraps-off-opteron-based-cluster", "https://www.rediff.com/money/report/cwg-prasar-bharti-earns/20101109.htm"]
            //     }
            // }
        },
        onLoadMore() {
            setTimeout(() => {
                this.resultShown = (this.resultShown.length + this.pageSize <= this.result.length) ? this.result.slice(0, this.resultShown.length + this.pageSize) : this.result
            }, Math.random() * 500 + 500)
        },
        showDrawer(index) {
            this.drawerVisible = true
            this.drawerText = this.result[index].text
        },
        closeDrawer(item) {
            console.log(item)
            this.drawerVisible = false
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
