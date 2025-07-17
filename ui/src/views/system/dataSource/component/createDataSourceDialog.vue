<template>
  <el-dialog
    v-model="dialogVisible"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    width="800"
    align-center
    class="member-dialog"
  >
    <template #header="{ titleId, titleClass }">
      <h4 :id="titleId" :class="titleClass">{{ $t('views.dataSource.addDataSource') }}</h4>
      <div class="dialog-sub-title">{{ $t('views.team.addSubTitle') }}</div>
    </template>

    <el-form 
    :model="form" 
    :rules="rules" 
    ref="formRef" 
    label-width="120px"
    class="vertical-label-form"
    label-position="left"
    style="max-height: 500px; overflow-y: auto; padding: 0 50px"
  >
    <!-- 基础信息 -->
    <el-form-item label="数据库类型" prop="db_type">
      <el-select v-model="form.db_type" placeholder="请选择">
        <el-option
          v-for="item in dbTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="数据源名称" prop="name" >
      <el-input v-model="form.name" />
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description" type="textarea" :rows="2" />
    </el-form-item>


    <el-form-item label="主机名/IP地址" prop="host">
      <el-input v-model="form.host" />
    </el-form-item>

    <el-form-item label="端口" prop="port">
      <el-input v-model="form.port" />
    </el-form-item>


    <el-form-item label="数据库名称" prop="database_name">
      <el-input v-model="form.database_name" />
    </el-form-item>


    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" />
    </el-form-item>

    <el-form-item label="密码" prop="password">
      <el-input v-model="form.password" show-password />
    </el-form-item>
    <el-form-item v-if="form.db_type == 'oracle'" prop="extra_params.oracle_connect_type" label="连接方式">
      <el-radio-group v-model="form.extra_params.oracle_connect_type">
        <el-radio label="sid">SID</el-radio>
        <el-radio label="service_name">服务名</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item
    v-if="form.db_type != 'mysql'"
    class="schema-label"
    prop="extra_params.schema"
    >
      <template v-slot:label>
        <el-button text size="small" @click="getDsSchema(formRef)" style="color: #0070ff; margin-left: 2px">
          <template #icon>
            <el-icon><Plus /></el-icon>
          </template>
          获取get_schema
        </el-button>
      </template>
      <el-select-v2
        v-model="form.extra_params.schema"
        :options="schemas"
        filterable
        :placeholder="请选择"
        class="de-select"
        @change="validatorSchema"
      />
    </el-form-item>
    <el-form-item v-if="form.db_type == 'oracle'" label="字符集" prop="extra_params.charset">
      <el-select v-model="form.extra_params.charset" placeholder="请选择">
        <el-option
          v-for="item in charset"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item v-if="form.db_type == 'oracle'" label="目标字符集" prop="extra_params.target_charset">
      <el-select v-model="form.extra_params.target_charset" placeholder="请选择">
        <el-option
          v-for="item in target_charset"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <!-- SSH 设置 -->
    <p  style="height: 40px;"> 
      <a style="color: #3370FF;">
        <span @click="showSSH = !showSSH">
        ssh 设置
        <el-icon v-if="!showSSH"><ArrowUp /></el-icon> 
        <el-icon v-else><ArrowDown /></el-icon>
        </span>
      </a>
    </p>
    
      <div v-if="showSSH">
        <el-form-item label="启用SSH" prop="ssh_enabled">
          <el-switch v-model="form.ssh_enabled" />
        </el-form-item>

        <template v-if="form.ssh_enabled">
          <el-form-item label="SSH主机" prop="ssh_config.host">
            <el-input v-model="form.ssh_config.host" />
          </el-form-item>
          <el-form-item label="SSH端口" prop="ssh_config.port">
            <el-input v-model="form.ssh_config.port" />
          </el-form-item>

          <el-form-item label="SSH用户名" prop="ssh_config.username">
            <el-input v-model="form.ssh_config.username" />
          </el-form-item>

          <el-form-item label="连接方式" prop="ssh_config.authType">
            <el-radio-group v-model="form.ssh_config.authType">
              <el-radio label="password">密码连接</el-radio>
              <el-radio label="key">SSH Key连接</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item 
            v-if="form.ssh_config.authType === 'password'"
            label="SSH密码" 
            prop="ssh_config.password"
          >
            <el-input v-model="form.ssh_config.password" show-password />
          </el-form-item>

          <el-form-item 
            v-if="form.ssh_config.authType === 'key'"
            label="SSH Key" 
            prop="ssh.key"
          >
            <el-input 
              v-model="form.ssh_config.key" 
              type="textarea" 
              :rows="4" 
              placeholder="粘贴您的SSH私钥"
            />
          </el-form-item>
        </template>
      </div>
        
      
      <!-- 高级配置 -->
        <p style="height: 40px;">
          <a style="color: #3370FF;font: 14px;">
            <span @click="showAdvance = !showAdvance">
            高级配置
            <el-icon v-if="!showAdvance"><ArrowUp /></el-icon> 
            <el-icon v-else><ArrowDown /></el-icon>
            </span>
          </a>
        </p>
        <div v-if="showAdvance">
          <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="初始连接数" prop="advanced.initialSize">
              <el-input-number
                v-model="form.advanced.initialSize"
                :min="1"
                :max="10"
                controls-position="right"
                @change="handleChange"
                style="width: 300px;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最小连接数" prop="advanced.minIdle">
              <el-input-number
                v-model="form.advanced.minIdle"
                :min="1"
                :max="10"
                controls-position="right"
                @change="handleChange"
                style="width: 300px;"
              />
            </el-form-item>
          </el-col>
          
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="最大连接数" prop="advanced.maxActive">
              <el-input-number
                v-model="form.advanced.maxActive"
                :min="1"
                :max="10"
                controls-position="right"
                @change="handleChange"
                style="width: 300px;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="查询超时(秒)" prop="advanced.queryTimeout">
              <el-input-number
                v-model="form.advanced.queryTimeout"
                :min="1"
                :max="10"
                controls-position="right"
                @change="handleChange"
                style="width: 300px;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        </div>
        

    <el-form-item>
      <el-button type="primary" @click="testConnect(formRef)" :loading="testLoading">测试连接</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitForm(formRef)" :loading="loading">
          {{ $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onMounted,reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess, MsgError } from '@/utils/message'
import dBSourceApi from '@/api/db-data-source'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])





const showSSH = ref(false)
const showAdvance = ref(false)
const activeCollapse = ref([])
const  dataSourceTableList = ref([])
const formRef = ref<FormInstance>()
const dbTypes = [
  { label: 'MySQL', value: 'mysql' },
  { label: 'PostgreSQL', value: 'postgresql' },
  { label: 'Oracle', value: 'oracle' }
]
const charset = ref(['GBK', 'BIG5', 'ISO-8859-1', 'UTF-8', 'UTF-16', 'CP850', 'EUC_JP', 'EUC_KR'])
const target_charset = ref(['GBK', 'UTF-8'])
const form = reactive({
  db_type: '',
  name: '',
  description: '',
  host: '',
  port: '',
  database_name: '',
  username: '',
  password: '',
  ssh_enabled: false,
  ssh_config: {
    host: '',
    port: '',
    username: '',
    authType: '',
    password: '',
    key: ''
  },
  advanced: {
    initialSize: '',
    minIdle: '',
    maxActive: '',
    queryTimeout: ''
  },
  extra_params:{
    schema:'',
    oracle_connect_type:'sid',
    charset:'',
    target_charset:''
  }
})
const rules = reactive({
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口号', trigger: 'blur' }],
  database_name: [{ required: true, message: '请输入数据库名称', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  'extra_params.schema': [{ 
    required: false, 
    message: '请选择schema', 
    trigger: ['blur', 'change'],
    validator: (rule: any, value: any, callback: any) => {
      // 只有非MySQL数据库且有schema选项时才验证
      if (form.db_type !== 'mysql' && schemas.value.length > 0 && !value) {
        callback(new Error('请选择schema'))
      } else {
        callback()
      }
    }
  }],
  ssh_config: {
    host: [{ required: true, message: '请输入SSH主机', trigger: 'blur' }],
    port: [{ required: true, message: '请输入SSH端口', trigger: 'blur' }],
    username: [{ required: true, message: '请输入SSH用户名', trigger: 'blur' }],
    password: [{ 
      required: true, 
      message: '请输入SSH密码', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.ssh_enabled && form.ssh_config.authType === 'password' && !value) {
          callback(new Error('请输入SSH密码'))
        } else {
          callback()
        }
      }
    }],
    key: [{ 
      required: true, 
      message: '请输入SSH Key', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.ssh_enabled && form.ssh_config.authType === 'key' && !value) {
          callback(new Error('请输入SSH Key'))
        } else {
          callback()
        }
      }
    }]
  },
  advanced: {
    maxActive: [
      { 
        validator: (rule, value, callback) => {
          if (value < form.advanced.minIdle) {
            callback(new Error('最大连接数不能小于最小连接数'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }
})
const schemas = ref([])
const resetForm = () => {
  formRef.value.resetFields()
}

const dialogVisible = ref<boolean>(false)

const memberForm = ref({
  users: []
})

const addMemberFormRef = ref<FormInstance>()

const loading = ref<boolean>(false)
const testLoading = ref<boolean>(false)


watch(dialogVisible, (bool) => {
  if (!bool) {
    memberForm.value = {
      users: []
    }
    loading.value = false
  }
})

// 监听数据库类型变化，设置默认端口
watch(() => form.db_type, (newType) => {
  if (newType === 'mysql') {
    form.port = '3306'
  } else if (newType === 'postgresql') {
    form.port = '5432'
  } else if (newType === 'oracle') {
    form.port = '1521'
  }
})

const open = () => {
  dialogVisible.value = true
  resetForm()
}
const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loading.value = true
      console.log("form111111111",form)
      dBSourceApi.addDataSource(form)
        .then((res) => {
          MsgSuccess(t('common.submitSuccess'))
          emit('refresh', [])
          dialogVisible.value = false
          loading.value = false
        })
        .catch(() => {
          loading.value = false
        })
    }
  })
}
const testConnect = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      testLoading.value = true
      dBSourceApi.testConnect(form)
        .then((res) => {
          MsgSuccess('连接成功')
          testLoading.value = false
        })
        .catch(() => {
          testLoading.value = false
        })
    }
  })
}
const getDsSchema = async () => {
  try {
    rules["extra_params.schema"] = { message: '请选择', trigger: 'blur'}
    await formRef.value.validate();
    const res = await dBSourceApi.SearchDataSourceSchema(form);
    schemas.value = res.data.map(item => ({ label: item, value: item }));
    MsgSuccess('Schema获取成功');
  } catch (error) {
    console.error('获取Schema失败:', error);
  }
};
const validatorSchema = (row:any) => {
  
}
onMounted(() => {})

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.member-dialog {
  .el-dialog__header {
    padding-bottom: 19px;
  }
}
.custom-select-multiple {
  width: 200%;
  .el-input {
    min-height: 100px;
  }
  .el-select__tags {
    top: 0;
    transform: none;
    padding-top: 8px;
  }
  .el-input__wrapper {
    align-items: start;
  }
}
.vertical-label-form .el-form-item {
  display: block !important; 
  margin-bottom: 18px; 
}

.vertical-label-form .el-form-item__label {
  display: block !important;
  float: none !important; 
  text-align: left !important;
  margin-bottom: 8px !important; 
  padding: 0 !important; 
  line-height: 1.5;
}

.vertical-label-form .el-form-item__content {
  margin-left: 0 !important; 
  display: block; 
}
.schema-label {
  .ed-form-item__label {
    display: flex !important;
    justify-content: space-between;
    padding-right: 0;

    &::after {
      display: none;
    }

    .name {
      .required::after {
        content: '*';
        color: #f54a45;
        margin-left: 2px;
      }
    }
  }
}
</style>
