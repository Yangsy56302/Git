# Baba Make Parabox

![Baba](logo/a8icon_240x160.png)![Make](logo/a8icon_240x160.png)![Parabox](logo/a8icon_240x160.png)

**Baba Make Parabox**（简称 **BMP**）是**Yangsy56302**以推箱子游戏[**Baba Is You**（by Arvi Hempuli）](https://hempuli.com/baba/)的机制为基础进行二次创作，缝合了另一个推箱子游戏[**Patrick's Parabox**（by Patrick Traynor）](https://www.patricksparabox.com/)的主要机制而做出的推箱子游戏，目前处于开发阶段。

**本游戏的源代码使用[MIT许可证](https://opensource.org/license/MIT/)。**
_……大概吧。_

**游戏使用[Pygame](https://www.pygame.org/news/)作为游戏引擎，而Pygame使用[GNU宽通用公共许可证 2.1版](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)。**
因此，本人不提供Pygame的源代码，而是提供使用未经修改的Pygame版本经[PyInstaller](https://pyinstaller.org/en/stable/index.html)打包后形成的游戏程序。

**PyInstaller使用[GNU通用公共许可证 第2版](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)。**

**本人并未拥有游戏纹理的所有权。**
如果您有关于游戏纹理的使用权等权利的更多信息，[请尽快联系我](#联系作者)。

该游戏的雏形诞生于2024.05.15，游戏文件夹创建时间为北京时间12:12:15。

## [更新日志](changelog.md)

请去查看`changelog.md`（段落标题就是链接）。

## 新手指南

### 下载

请跳转到[Github](https://github.com/Yangsy56302/BabaMakeParabox)，
点击页面右上方写着**Code**的绿色按钮，在展开的下拉菜单里点击最靠下的的**Download zip**即可下载所需的压缩包。
您也可以点击[此链接](https://github.com/Yangsy56302/BabaMakeParabox/archive/refs/heads/main.zip)以直接下载。

压缩包（`BabaMakeParabox-main.zip`）内含有**可执行程序（bmp.exe）**，**源代码（BabaMakeParabox/）**，
**Baba Make Parabox 添加的新纹理（sprites_new/）**， **Baba Is You 的部分音效（sounds/）** 等内容。

备用下载地址包括需要特殊手段访问的[Gitlab](https://gitlab.com/Yangsy56302/BabaMakeParabox)，
以及需要注册账号才能下载的[Gitee](https://gitee.com/Yangsy56302/BabaMakeParabox)。

### 安装

+ **推荐方式**
    1. 在您准备安装的位置（如`C:\Program Files\`）新建文件夹；
    2. 将压缩包`BabaMakeParabox-main.zip`内的文件和文件夹解压到第 1 步新建的文件夹内；
    3. 在第 2 步解压的文件中找到`baba-is-you-original-sprites.zip`（**Baba Is You** 本体的纹理），解压到与第 2 步相同的文件夹内；
    4. 找到文件夹`sprites_old`，并将其重命名为`sprites`；
    5. 找到文件夹`sprites_new`，并将里面的所有文件转移到在第 4 步被重命名的文件夹（`sprites`，重命名前称为`sprites_old`）里面。
+ **备用方式**
    1. 完成**推荐方式**的所有步骤；
    2. 通过以下任意一种方式安装**Python**：
        + 官方安装方式
            1. 进入[Python 官方网站](https://www.python.org)；
            2. 找到位于Logo右下方的**Downloads**，悬停展开；
            3. 在展开后的部分找到**Download for Windows**下方的按钮，点击以下载；
            4. 打开下载完成的安装程序，勾选最下方的**Add python.exe to PATH**，然后点击醒目的**Install Now**以安装Python；
            5. 等待安装完成，然后重启电脑。
        + _（待补）_
    3. 运行`inst-win.bat`，然后耐心等待几分钟，直到文件夹内出现`bmp.exe`和`submp.exe`。

### 运行

双击运行`play-win.bat`，这将会间接运行`bmp.exe`，然后启动程序。
直接运行`bmp.exe`也是可行的，但程序故障后会直接关闭终端窗口，所以不推荐。
如果您的**Windows**系统安装了**Python**，或者您使用了备用方式来安装游戏，那么还可以尝试运行`run-win.bat`来启动游戏。

由于游戏目前仍然处于开发阶段，Baba Make Parabox 暂未制作大型关卡包，
不过早期版本遗留的测试用关卡包文件，在手动更新后仍能使用
（其中包括一个由[彩虹箱RainbowBox](https://space.bilibili.com/1281976796/)所制作的[玩法测试关卡包](levelpacks/mikan.json)）。

迫切于体验新版本更新内容的玩家可以[**自行制作关卡包**](#编辑器)。

**游戏仅在命令行窗口存在且未选中内部文本时正常运行。**

游戏未响应时，请先在命令行内 **取消选中文字** ，
确保游戏 **并未询问输入** ，
然后耐心 **等待十秒左右** 直至游戏继续运行。

如果游戏仍然处于未响应状态或在一段时间后崩溃，则可以确认该现象是一个游戏漏洞。

## 游戏内容

### 控制

+ **`W` / `S` / `A` / `D`**：移动
+ **`SPACE`**：等待
+ **`ESC`**：回到上层关卡
+ **`Z`**：撤销
+ **`CTRL` + `R`**：重新开始关卡包
+ **`O`**：载入临时存档
    + **`CTRL` + `...`**：可指定此临时存档的名字
+ **`P`**：保存临时存档
    + **`CTRL` + `...`**：可指定此临时存档的名字
+ **`TAB`**：显示各种信息
+ **`F1`**: 显示FPS
+ **鼠标左键**：进入空间
+ **鼠标右键**：回到上层空间
+ **鼠标滚轮**：循环选择空间
+ **关闭游戏窗口**：停止游玩，指定文件名以保存
+ **关闭终端**：强制退出程序

## 编辑器

该章节暂不提供有关如何设计谜题等问题的信息。

### 控制

+ **鼠标左键**：放置物体
    + **`SHIFT` + `...`**：即使该位置存在物体也额外放置
    + **`CTRL` + `...`**：设置部分物体的额外信息 **\***
    + **`ALT` + `...`**：进入空间
        + **`SHIFT` + `...`**：进入关卡
+ **鼠标右键**：删除物体
    + **`ALT` + `...`**：回到上层空间
        + **`SHIFT` + `...`**：回到上层关卡
+ **鼠标滚轮**：循环选择物体类型
    + **`SHIFT` + 鼠标滚轮向上滚动**：选择该物体的名词
    + **`SHIFT` + 鼠标滚轮向下滚动**：选择该名词指向的物体
    + **`ALT` + `...`**：循环选择空间
        + **`SHIFT` + `...`**：循环选择关卡
+ **(`W` / `S` / `A` / `D`) / 方向键**：选择物体朝向
+ **`0` ~ `9`**：从快捷栏选择物体类型
    + **`SHIFT` + `...`**：设置快捷栏的物体类型
+ **`N`**：新建空间 **\***
    + **`ALT` + `...`**：新建关卡 **\***
+ **`M`**：删除空间 **\***
    + **`ALT` + `...`**：删除关卡 **\***
+ **`R`**：设置全局规则 **\***
    + **`SHIFT` + `...`**：删除全局规则 **\***
+ **`T`**：设置所处空间的标识符 **\***
    + **`ALT` + `...`**：设置所处关卡的标识符 **\***
+ **`CTRL` + (`X` / `C` / `V`)**：剪切 / 复制 / 粘贴 光标上的物体
+ **`F1`**: 显示FPS
+ **关闭游戏窗口**：退出编辑器，指定文件名以保存
+ **关闭终端**：强制退出程序

**注意：带有 \* 的键位提示代表按下该键之后需要在终端内输入更多信息。**
此时游戏窗口会停止响应，信息输入完成后会恢复。

**放置的空间、克隆和关卡默认指向摄像头所在的空间和关卡。**

## 杂项

### 计划实现

+ **就在下期**
    + 在游戏代码以外的位置定义常规物体。
        + 将在`4.01`或`4.002`更新时添加。
+ **短期**
    + 文本可以跨空间组成规则。
    + 优化关卡包存储格式。
+ **中期**
    + `GROUP`的运作逻辑。
    + 优化关卡游玩流程。
        + 收藏品改为一般物体而非独立类型。
        + _或许会参考 Maxwell's Puzzling Demon 的部分机制。_
    + GUI（图形用户界面）。
        + 使用可输入文本的游戏窗口取代命令行的显示。
    + 纯装饰属性，如`RED`、`BLUE`等颜色。
+ **长期**
    + _`GAME`的复杂语法。_
        + 目前对`GAME`应用修饰词会使其不指代任何物体。
    + `Infinite Loop`与其检测方法。
+ **遥遥无期**
    + 官方关卡包……？

### 异常情况分类

#### 游戏特性

+ 属性前带有多个`NOT`的规则只会否定一条恰好缺少一个`NOT`的规则。
    + 例如，`BABA IS NOT YOU`否定一条`BABA IS YOU`；`BABA IS NOT NOT YOU`否定一条`BABA IS NOT YOU`，可能导致已有的`BABA IS YOU`不再被那条`BABA IS NOT YOU`否定。
+ `FEELING`每轮只检测一次，以试图避免检测停机问题和判定无限循环。
+ `WORD`属性对`TEXT`有效。

#### 游戏漏洞

+ 游戏过程中，即使镜头所在空间的方向更改，鼠标仍会使用默认方向。
+ 移动系统的完成度很低，有时表现会与预期不同，主要出现在多个物体同时移动的情况下。
    + 例如，多个常规空间物体同时存在时，物体进入该空间所复制出的新物体的数量。

## 联系作者

哔哩哔哩：**<https://space.bilibili.com/430612354>**

QQ：**2485385799**

163邮箱：**<yangsy56302@163.com>**