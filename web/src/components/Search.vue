<template>
    <div class="search">
        <a-row type="flex" justify="start">
            <a-col :span="12">
                <a-row type="flex" justify="start" style="margin-top: 30px;">
                    <a-col>
                    <template>
                    <a-popover>
                        <template #content>
                        <p>To activate the Boolean query, use</p>
                        <pre>(expr)</pre>
                        <pre>[keywords]</pre>
                        </template>
                        <a-tag color="blue" style="font-size: 100%; font-family: Consolas, monospace;" v-if="isBoolean">Boolean Search</a-tag>
                        <a-tag color="green" style="font-size: 100%; font-family: Consolas, monospace;" v-else>Ranked Search</a-tag>
                    </a-popover>
                    </template>
                    </a-col>
                </a-row>
                <a-row>
                    <a-input-search v-model="searchContent" placeholder="Enter query here..." enter-button @search="onSearch" @change="handleInput" style="width: 100%; margin-top: 10px;"/>
                </a-row>
            </a-col>
        </a-row>
        <a-row type="flex" justify="left" v-if="code !== 0 && code != 200">
            <a-col :span="12">
                <a-tag type="flex" justify="center" color="red">{{ code }} {{ msg }}.</a-tag>
            </a-col>
        </a-row>
        <!--<a-row type="flex" justify="center">
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
        </a-row>-->
        <!-- a long split horizontal line -->
        <a-row>
            <a-divider style="margin-top: 20px; margin-bottom: 20px;"></a-divider>
        </a-row>
        <a-row>
            <a-col :span="16">
                <a-row type="flex" justify="start" v-if="code === 200">{{ type }} search: {{ totalResult }} results in {{ latency }} second.</a-row>
                <a-row type="flex" justify="center">
                    <a-list
                        class="demo-loadmore-list"
                        :loading="isLoadingSearch"
                        item-layout="horizontal"
                        :data-source="resultShown"
                        style="margin-top: 20px;"
                    >
                        <a-spin v-if="isLoadingSearch" size="large"/>
                        <div
                            v-if="showLoadingMore"
                            slot="loadMore"
                            :style="{marginTop: '12px', height: '32px', lineHeight: '32px' }"
                        >
                            <a-button @click="onLoadMore">
                                More...
                            </a-button>
                        </div>
                        <a-list-item slot="renderItem" slot-scope="item, index">
                            <a-list-item-meta
                            >
                                <a-row slot="title" type="flex" justify="start">
                                    <a-col :span="9.5" style="text-align: start;font-size: 125%;">
                                        <a-tag color="blue" style="font-size: 100%;">
                                            <a :href="item.url" style="color: rgb(45, 183, 245);">{{ getHostname(item.url) }}</a>
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
                                <div slot="description" style="text-align: start;"><div v-html="item.brief"></div></div>
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
                                    <div style="text-align: start; font-family: Consolas, monospace;">
                                        <a-card title="Ask me anything!">
                                        <a-input-search
                                            v-model="QAContent"
                                            placeholder="When did the news publish?"
                                            enter-button="Ask"
                                            :loading="isLoadingQA"
                                            size="large"
                                            @search="onQA"
                                        />
                                        <div v-if="qa.answer">
                                            <a-comment>
                                                <template #author><a>RoBERTa</a></template>
                                                    <template #avatar>
                                                        <a-avatar
                                                            shape="square"
                                                            size="large"
                                                            style="verticalAlign: 'middle'">🤖</a-avatar>
                                                    </template>
                                                    <template #content>
                                                    <a-card :loading="isLoadingQA" style="font-size: 150%;">
                                                        {{ qa.answer }}
                                                    </a-card>
                                                    </template>
                                                    <template #datetime>
                                                    <a-tooltip>
                                                        in {{qa.time}} seconds
                                                    </a-tooltip>
                                                </template>
                                            </a-comment>
                                        </div>
                                        </a-card>
                                        
                                        <a-divider ></a-divider>

                                        <strong>Link:</strong>&nbsp;&nbsp;
                                        <a-tag color="blue" style="font-size: 100%;">
                                            <a :href="drawerUrl" style="color: rgb(45, 183, 245);">{{ drawerUrl.substring(0, 50) + (drawerUrl.length > 50 ? '...' : '') }}</a>
                                        </a-tag>
                                        <br/>
                                        <strong>Time:</strong>&nbsp;&nbsp;
                                        <a-tag color="cyan" style="font-size: 100%">{{ drawerTimestamp }}</a-tag>
                                        <br/>
                                        <strong>Body:</strong>
                                    </div>
                                    <div v-html="drawerBody"></div>
                                </a-drawer>
                            </div>
                        <!-- <div>{{ item.text }}</div> -->
                        </a-list-item>
                    </a-list>
                </a-row>
            </a-col>
            <a-col :span="8">
                <a-card :loading="isLoadingSummary" title="Summarization">
                    <p>
                        {{summary.summary_text}}
                    </p>
                    <p style="text-align: end; color: gray;" v-if="summary.time">
                        Generated in {{ summary.time }} second.
                    </p>
                </a-card>
            </a-col>
        </a-row>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data(){
        return {
            isLoadingSearch: false,
            isLoadingSummary : false,
            isLoadingQA: false,
            showLoadingMore: false,
            drawerVisible: false,
            drawerBody: '',
            drawerUrl: '',
            drawerTimestamp: '',
            totalResults: 0,
            activeKey1: [],
            activeKey2: [],
            result: [],
            resultShown: [],
            totalResult: 0,
            pageSize: 5,
            summary: {},
            qa: {'answer' : '', 'time': undefined},
            latency: 0,
            type: '',
            code: 0,
            msg: 'Initialize',
            isBoolean: false,
            searchContent: '',
            QAContent: '',
        }
    },
    mounted() {
        this.isLoadingSearch = false
        if (typeof(this.$route.query.query) != 'undefined') {
            this.searchContent = this.$route.query.query
            if (this.searchContent.length > 0) {
                this.getData('query', this.searchContent)
            }
        }
        this.handleInput()
    },
    name: 'Search',
    watch: {
        $route(to, from) {
            console.log(to, from)
            this.searchContent = to.query.query
            if (typeof(this.$route.query.query) != 'undefined') {
                this.getData('query', to.query.query)
            }
        }
    },
    methods: {
        onSearch(value) {
            this.$router.push({
                path: '/search',
                query: {
                    query: value
                }
            })
            // this.getData('query', value)
        },
        getData(type, query) {
            this.isLoadingSearch = true
            this.isLoadingSummary = true
            var input = {'type': type, 'query': query}
            console.log('input', input)
            axios.post('http://127.0.0.1:5000/search', input).then(res => {
                console.log(res)
                this.code = res.data.code
                this.msg = res.data.msg
                if (res.data.code != 200) {
                    this.result = []
                    this.totalResult = 0
                    this.summary = {}
                    this.qa = {}
                } else {
                    this.result = res.data.result
                    this.latency = res.data.time
                    this.type = res.data.type
                    this.totalResult = res.data.cnt
                    if (typeof(res.data.summary) == 'undefined') {
                        this.summary = {}
                    } else {
                        this.summary = res.data.summary
                        console.log(this.summary)
                    }
                    if (typeof(res.data.qa) == 'undefined') {
                        this.qa = {}
                    } else {
                        this.qa = res.data.qa
                    }
                }
                this.isLoadingSearch = false
                this.resultShown = []
                this.onLoadMore()
                if (res.data.type != 'Boolean')
                {   
                    // summarize
                    axios.post('http://127.0.0.1:5000/summary', input).then(res => {
                        if (res.data.code == 200) {
                            if (typeof(res.data.summary) == 'undefined') {
                                this.summary = {'summary_text': '', 'time': '0'}
                            } else {
                                this.summary = res.data.summary
                            }
                        }
                        this.isLoadingSummary = false
                    })
                } else {
                    this.isLoadingSummary = false
                    this.summary = {'summary_text': 'Summarization disabled for Boolean Search.', 'time': undefined}
                }
            })
        },
        onLoadMore() {
            this.resultShown = (this.resultShown.length + this.pageSize <= this.result.length) ? this.result.slice(0, this.resultShown.length + this.pageSize) : this.result
            this.showLoadingMore = this.resultShown.length < this.result.length
            console.log(this.resultShown)
            console.log(this.isLoadingSearch)
            console.log(this.showLoadingMore)
        },
        showDrawer(index) {
            this.drawerVisible = true
            this.drawerUrl = this.result[index].url
            this.drawerTimestamp = this.result[index].timestamp
            this.drawerBody = this.result[index].body
            this.drawerText = this.result[index].text
        },
        onQA() {
            this.isLoadingQA = true
            var input = {'question': this.QAContent, 'context' : "Link: " + this.drawerUrl + "Time: " + this.drawerTimestamp + this.drawerText}
            axios.post('http://127.0.0.1:5000/qa', input).then(res => {
                this.isLoadingQA = false
                if (typeof(res.data.answer) == 'undefined') {
                    this.qa = {'answer' : '', time : 0}
                } else {
                    this.qa = res.data.answer
                }
            })
        },
        closeDrawer(item) {
            console.log(item)
            this.drawerVisible = false
            this.qa = {'answer' : '', time : 0}
            this.QAContent = ''
        },
        handleInput(value) {
            setTimeout(() => {
                let query = this.searchContent
                if (query.length > 1 && (query[0] == '(' && query[query.length - 1] == ')') || (query[0] == '[' && query[query.length - 1] == ']')) {
                    this.isBoolean = true
                } else {
                    this.isBoolean = false
                }
            }, 0, value)
        },
        getHostname(url) {
            const hostname = new URL(url).hostname;
            return hostname;
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
