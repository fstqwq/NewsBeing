<template>
    <div class="chat">
        <a-row type="flex" justify="center">
            <a-col :span="12">
                <a-row type="flex" justify="center" style="margin-top: 30px;">
                    <a-tag color="purple" style="font-size: 100%; font-family: Consolas, monospace;">Advanced Search</a-tag>
                </a-row>
                <a-row>
                    <a-input-search v-model="searchContent" placeholder="Chat here..." enter-button @search="onChat"  style="width: 100%; margin-top: 10px;"/>
                </a-row>
            </a-col>
        </a-row>
        <a-row type="flex" justify="center" v-if="code !== 0 && code != 200">
            <a-col :span="12">
                <a-tag type="flex" justify="center" color="red">{{ code }} {{ msg }}.</a-tag>
            </a-col>
        </a-row>
        <a-row>
            <a-divider style="margin-top: 20px; margin-bottom: 20px;"></a-divider>
        </a-row>
        <a-row  type="flex" justify="center">
            <a-col :span="12">
                    <a-card :loading="isChatKeywordsLoading">
                    <p v-if="chat.keywords" style="text-align: start;">
                        Searching for: <strong>{{chat.keywords}}</strong>
                    </p>
                    <a-comment style="text-align: start;">
                    <template #author><a>News Being</a></template>
                        <template #avatar>
                            <a-avatar
                                shape="square"
                                size="large"
                                style="verticalAlign: middle">🤖</a-avatar>
                        </template>
                        <template #content>
                        <a-card :loading="isChatAnswerLoading" style="font-size: 150%;">
                            {{ chat.answer ? chat.answer : 'Hello, I am News Being. Ask me anything!' }}
                        </a-card>
                        </template>
                        <template #datetime>
                        <a-tooltip v-if="chat.time">
                            in {{chat.time}} seconds
                        </a-tooltip>
                        </template>
                    </a-comment>
                    </a-card>
                </a-col>
        </a-row>
        <a-row>
            <a-divider style="margin-top: 20px; margin-bottom: 20px;"></a-divider>
        </a-row>
        <a-row type="flex" justify="center">
            <a-col :span="16" justify="center">
                <a-row type="flex" justify="center" v-if="code === 200">Search finished in {{ latency }} second.</a-row>
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
                                        <div v-if="qa.answer"  :loading="isLoadingQA">
                                        <a-comment>
                                        <template #author><a>RoBERTa</a></template>
                                            <template #avatar>
                                                <a-avatar
                                                    shape="square"
                                                    size="large"
                                                    style="verticalAlign: middle">🤖</a-avatar>
                                            </template>
                                            <template #content>
                                            <p>
                                                {{ qa.answer }}
                                            </p>
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
        </a-row>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    data(){
        return {
            isLoadingSearch: false,
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
            qa: {},
            chat: {},
            latency: 0,
            type: '',
            code: 0,
            msg: 'Initialize',
            isBoolean: false,
            isChatKeywordsLoading: false,
            isChatAnswerLoading: false,
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
        } else {
            this.searchContent = ''
        }
    },
    name: 'Chat',
    watch: {
        $route(to, from) {
            console.log(to, from)
            this.searchContent = to.query.query
        }
    },
    methods: {
        onChat(value) {
            this.$router.push({
                path: '/chat',
                query: {
                    query: value
                }
            })
            this.getData('query', value)
        },
        getData(type, query) {
            this.isLoadingSearch = true
            this.isChatAnswerLoading = true
            this.isChatKeywordsLoading = true
            this.resultShown = []
            this.chat = {}
            var input = {'query': query}
            console.log('input', input)
            axios.post('http://127.0.0.1:5000/extract', input).then(res => {
                this.isChatKeywordsLoading = false
                console.log(res)
                this.code = res.data.code
                this.msg = res.data.msg
                if (res.data.code != 200) {
                    this.chat.keywords = 'Error: ' + res.data.msg
                } else {
                    this.chat.keywords = res.data.keywords
                    input = {'query' : this.chat.keywords} 
                    axios.post('http://127.0.0.1:5000/search', input).then(res=> {
                        this.result = res.data.result.slice(0, 5)
                        this.latency = res.data.time
                        this.type = res.data.type
                        this.totalResult = res.data.cnt
                        this.isLoadingSearch = false
                        this.onLoadMore()
                        input = {'question': this.searchContent, 'keywords' : this.chat.keywords}
                        axios.post('http://127.0.0.1:5000/chat', input).then(res => {
                            this.isChatAnswerLoading = false
                            this.chat.answer = res.data.answer.answer
                            this.chat.time = res.data.answer.time
                        })
                    })
                }
            })
        },
        onLoadMore() {
            this.resultShown = (this.resultShown.length + this.pageSize <= this.result.length) ? this.result.slice(0, this.resultShown.length + this.pageSize) : this.result
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
