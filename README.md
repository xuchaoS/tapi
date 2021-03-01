##### Tapi 简单接口自动化测试框架

###### 简要说明
1. 使用python + pytest + requests + allure集成的接口测试框架
2. 可以使用Excel编写测试用例，自动生成测试脚本代码，并使用pytest执行测试脚本，形成allure报告，查看测试结果
3. 支持使用fiddler进行用例录制，进行简单编辑后可以直接作为使用

###### 使用方法
1. 参考test_cases文件夹中的样例编写测试用例，编写好的文件存放在test_cases文件夹中
2. 使用执行main文件执行所有excel编写的测试用例

###### 测试用例编写说明
1. 用例名称：非必须，指定测试用例名称，同一个sheet页中不能重复，如果为空则表示改行为上面测试用例的一个步骤，特殊名称：`setup`，`teardown`，`setup_class`，`teardown_class`
2. run：用例名称不为空时必须，执行标志，指定测试用例是否执行，`Y`或`N`
3. 用例级别：用例名称不为空时必须，指定用例级别，枚举值： `blocker`、`critical`、`normal`、`minor`、`trivial`
4. 标签：非必须，指定用例标签，多个标签使用换行分隔
5. 变量引入：非必须，在接口调用前进行变量赋值等操作，编写格式为单行python代码，不支持多行缩进，多行会视为多个单行代码
6. 请求地址：用例名称为非特殊名称时必须，可以使用f字符串表达式进入变量，即{变量}
7. method：用例名称为非特殊名称时必须
8. headers: 用例名称为非特殊名称时必须，支持python字典和json两种数据格式，使用变量时仅支持python字典
9. query：非必须，get请求参数，支持python字典和json两种数据格式，使用变量时仅支持python字典
10. body: 非必须，post请求参数，支持python字典和json两种数据格式，使用变量时仅支持python字典
11. 预期结果：非必须，请求结果进行验证，使用单行python代码，每一行需要返回布尔值，可以使用r变量表示requests的返回值
12. 变量导出：非必须，在接口调用后进行变量赋值等操作，编写格式为单行python代码，不支持多行缩进，多行会视为多个单行代码
13. 在所有可以使用变量的字段中提供var作为全局变量，在用例之间进行传递

###### 用例录制
1. 使用fiddler进行抓包
2. 在fiddler中选择需要的请求，点击File -> Export Sessions -> Selected Sessions...，选择HTTPArchive v1.2进行导出
3. 使用har2xlsx函数将导出的har文件转换为测试用例的Excel文件，同时生成config文件
4. 对导出的测试用例进行个性化编辑

###### 依赖
1. python 3.7+
2. pycharm
3. `pip install -r requirements.txt`
4. allure

###### pycharm环境配置
1. 配置 -> python集成工具 -> 测试 ，修改为pytest
2. 运行/调试配置 -> Templates -> Python测试 -> pytest -> 其他参数，修改为`--alluredir .\outputs\allure -vs --clean-alluredir`
3. 运行/调试配置 -> Templates -> Python测试 -> pytest -> 工作目录，修改为当前本地的项目目录

###### 单个用例调试
* 进行如上配置后，可以在首次执行main.py后，看到自动生成的测试脚本test_scripts_...，打开脚本可以点击用例左侧的执行按钮进行单个用例的执行、调试，调试完毕后需要返回去修改excel测试用例

###### 查看测试报告
1. main函数使用`True`参数时会在测试结束后自动打开测试报告，会阻塞测试进程执行，直至手动关闭报告服务
2. 在命令行中使用`allure serve outputs\allure`开启测试报告服务，每次执行测试用例后如果需要查看最新报告，需要重新执行该命令

