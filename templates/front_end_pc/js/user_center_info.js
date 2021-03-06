var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        email_error: false,
        histories: [],
    },
    mounted: function () {


        // 获取个人信息:
        this.get_person_info()

        this.get_history()
    },
    methods: {
          // 退出登录按钮
        logoutfunc: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = 'login.html';
        },
        get_history:function(){
             // 添加下列代码, 发送请求, 获取用户的浏览记录信息:
            axios.get(this.host + '/browse_histories/', {
                    // 向后端传递JWT token的方法
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials:true,
                })
                .then(response => {
                    this.histories = response.data;
                    for (var i = 0; i < this.histories.length; i++) {
                        this.histories[i].url = '/goods/' + this.histories[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error)
                });
        },
        // 获取用户所有的资料
        get_person_info: function () {
            var url = this.host + '/info/';
            axios.get(url, {
                // 向后端传递JWT token的方法
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    this.username = response.data.username;
                    this.mobile = response.data.mobile;
                    this.email = response.data.email;
                    this.email_active = response.data.email_active;
                })
                .catch(error => {
                    if (error.response.status == 401 || error.response.status == 403) {
                        location.href = '/login.html?next=/user_center_info.html';
                    }
                })
        },
        // 保存email
        save_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
                return;
            }

            // 进行前端页面请求:
            var url = this.host + '/emails/'
            axios.put(url,
                {email: this.email},
                {
                    // 向后端传递JWT token的方法
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                    withCredentials: true

                })
                // 成功请求的回调
                .then(response => {
                    this.set_email = false;
                    this.send_email_btn_disabled = true;
                    this.send_email_tip = '已发送验证邮件'
                })
                // 失败请求的回调:
                .catch(error => {
                    alert('请求失败, 失败原因:', error);
                });
        }
    }
});