import flet as ft
from flet import Colors
from vultr_api import VultrAPI
from config_manager import ConfigManager
import math

class VultrManager:
    PANEL_WIDTH = 400
    FIELD_WIDTH = 360
    LIST_HEIGHT = 390

    def __init__(self, page: ft.Page):
        self.page = page
        self.config_manager = ConfigManager()
        self.api = None

        self.palette = {
            "bg": "#f4f7fb",
            "panel": "#ffffff",
            "panel_alt": "#f1f5f9",
            "line": "#e2e8f0",
            "text": "#0f172a",
            "muted": "#64748b",
            "accent": "#1f6feb",
            "accent_alt": "#0ea5e9",
            "success": "#16a34a",
            "warning": "#f59e0b",
            "danger": "#dc2626"
        }
        self.panel_shadow = [
            ft.BoxShadow(
                blur_radius=12,
                color=Colors.BLACK12,
                offset=ft.Offset(0, 4)
            )
        ]
        self.card_shadow = [
            ft.BoxShadow(
                blur_radius=8,
                color=Colors.BLACK12,
                offset=ft.Offset(0, 2)
            )
        ]
        self.password_placeholder = "正在初始化..."

        # Window configuration
        self.page.window.icon = "icon.ico"
        self.page.title = "Vultr 服务器管理器"
        self.page.window.width = 920
        self.page.window.height = 750
        self.page.window.resizable = False
        self.page.window.maximizable = False
        self.page.padding = 12
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            font_family="Microsoft YaHei UI",
            color_scheme_seed=self.palette["accent"]
        )
        self.page.bgcolor = self.palette["bg"]

        # Pagination
        self.current_page = 1
        self.items_per_page = 2
        self.total_servers = []

        # UI components
        self.api_key_input = None
        self.region_dropdown = None
        self.plan_dropdown = None
        self.os_dropdown = None
        self.status_text = None
        self.servers_column = None
        self.page_text = None
        self.prev_btn = None
        self.next_btn = None
        self.announcement = None
        self.busy_indicator = None
        self.server_count_text = None
        self.save_btn = None
        self.query_all_btn = None
        self.buy_btn = None
        self.refresh_btn = None
        self.action_controls = []

        self.setup_ui()

        # Load saved API key
        saved_key = self.config_manager.get_api_key()
        if saved_key:
            self.api_key_input.value = saved_key
            self.api = VultrAPI(saved_key)

    def setup_ui(self):
        header = self.create_header()
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()

        self.announcement = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ANNOUNCEMENT_OUTLINED, color=self.palette["warning"], size=18),
                ft.Column([
                    ft.Text("欢迎使用 Vultr 管理器", size=12, weight=ft.FontWeight.BOLD, color=self.palette["text"]),
                    ft.Text(
                        "创建实例、重装系统、查看资源状态。更多详情请访问项目主页。",
                        size=11,
                        color=self.palette["muted"]
                    )
                ], spacing=2, expand=True),
                ft.TextButton("项目主页", on_click=self.open_official_site),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=10),
            bgcolor="#fff7ed",
            border=ft.border.all(1, "#fed7aa"),
            border_radius=10,
            padding=12,
        )

        main_layout = ft.Column([
            header,
            ft.Row([
                left_panel,
                ft.VerticalDivider(width=1, color=self.palette["line"]),
                right_panel
            ], spacing=10, expand=True),
            self.announcement
        ], spacing=12, expand=True)

        self.page.add(main_layout)

        self.action_controls = [
            self.api_key_input,
            self.region_dropdown,
            self.plan_dropdown,
            self.os_dropdown,
            self.save_btn,
            self.query_all_btn,
            self.buy_btn,
            self.refresh_btn
        ]

    def create_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.CLOUD_OUTLINED, color=self.palette["accent"], size=26),
                    ft.Column([
                        ft.Text("Vultr 服务器管理器", size=20, weight=ft.FontWeight.BOLD, color=self.palette["text"]),
                        ft.Text("一站式创建、重装与管理服务器", size=11, color=self.palette["muted"]),
                    ], spacing=2)
                ], spacing=10),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_OUTLINED, size=16, color=self.palette["muted"]),
                        ft.Text("API 密钥已本地保存", size=11, color=self.palette["muted"])
                    ], spacing=6),
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border_radius=18,
                    bgcolor=self.palette["panel_alt"]
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=12,
            bgcolor=self.palette["panel"],
            border=ft.border.all(1, self.palette["line"]),
            shadow=self.panel_shadow
        )

    def section_header(self, title, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=self.palette["accent"], size=18),
                ft.Text(title, size=13, weight=ft.FontWeight.BOLD, color=self.palette["text"])
            ], spacing=6),
            bgcolor=self.palette["panel_alt"],
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            border_radius=8
        )

    def build_action_button(self, label, icon, bgcolor, on_click, width=None, height=40):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, size=16, color=Colors.WHITE),
                ft.Text(label, size=12, color=Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            on_click=on_click,
            width=width or self.FIELD_WIDTH,
            height=height,
            bgcolor=bgcolor
        )

    def create_left_panel(self):
        self.api_key_input = ft.TextField(
            label="API 密钥",
            hint_text="请输入 Vultr API 密钥",
            width=self.FIELD_WIDTH,
            password=True,
            can_reveal_password=True,
            border_color=self.palette["line"],
            border_radius=8
        )

        self.save_btn = self.build_action_button(
            "保存配置",
            ft.Icons.SAVE_OUTLINED,
            self.palette["accent"],
            self.save_api_key
        )

        self.region_dropdown = ft.Dropdown(
            label="选择区域",
            width=self.FIELD_WIDTH,
            options=[],
            border_color=self.palette["line"],
            border_radius=8
        )

        self.plan_dropdown = ft.Dropdown(
            label="选择套餐（≤ $5/月）",
            width=self.FIELD_WIDTH,
            options=[],
            border_color=self.palette["line"],
            border_radius=8
        )

        self.os_dropdown = ft.Dropdown(
            label="选择系统",
            width=self.FIELD_WIDTH,
            options=[],
            border_color=self.palette["line"],
            border_radius=8
        )

        self.query_all_btn = self.build_action_button(
            "一键获取",
            ft.Icons.SEARCH,
            "#2563eb",
            self.query_all
        )

        self.buy_btn = self.build_action_button(
            "立即购买",
            ft.Icons.SHOPPING_CART_OUTLINED,
            "#0f766e",
            self.buy_server
        )

        self.busy_indicator = ft.ProgressRing(
            width=16,
            height=16,
            stroke_width=2,
            visible=False,
            color=self.palette["accent"]
        )
        self.status_text = ft.Text(
            value="就绪",
            size=11,
            color=self.palette["muted"],
            width=self.FIELD_WIDTH - 20
        )
        status_row = ft.Row([
            self.busy_indicator,
            self.status_text
        ], spacing=6)

        return ft.Container(
            content=ft.Column([
                self.section_header("API 设置", ft.Icons.KEY_OUTLINED),
                self.api_key_input,
                self.save_btn,

                ft.Container(height=6),

                self.section_header("购买服务器", ft.Icons.SHOPPING_BAG_OUTLINED),
                self.query_all_btn,
                self.region_dropdown,
                self.plan_dropdown,
                self.os_dropdown,
                self.buy_btn,
                status_row,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            width=self.PANEL_WIDTH,
            padding=12,
            bgcolor=self.palette["panel"],
            border_radius=12,
            border=ft.border.all(1, self.palette["line"]),
            shadow=self.panel_shadow
        )

    def create_right_panel(self):
        self.servers_column = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

        self.server_count_text = ft.Text("共 0 台", size=11, color=self.palette["muted"])
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE_OUTLINED, color=self.palette["accent"], size=18),
                    ft.Text("我的服务器", size=13, weight=ft.FontWeight.BOLD, color=self.palette["text"])
                ], spacing=6),
                self.server_count_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=self.palette["panel_alt"],
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            border_radius=8
        )

        self.prev_btn = ft.ElevatedButton(
            text="上一页",
            on_click=self.prev_page,
            disabled=True,
            width=120,
            height=32,
            bgcolor=self.palette["panel_alt"],
            color=self.palette["text"]
        )

        self.page_text = ft.Text("第 1 页", size=11, color=self.palette["muted"], weight=ft.FontWeight.BOLD)

        self.next_btn = ft.ElevatedButton(
            text="下一页",
            on_click=self.next_page,
            disabled=True,
            width=120,
            height=32,
            bgcolor=self.palette["panel_alt"],
            color=self.palette["text"]
        )

        pagination = ft.Row([
            self.prev_btn,
            ft.Container(
                content=self.page_text,
                width=100,
                alignment=ft.alignment.center
            ),
            self.next_btn
        ], alignment=ft.MainAxisAlignment.CENTER)

        self.refresh_btn = self.build_action_button(
            "刷新列表",
            ft.Icons.REFRESH,
            self.palette["accent_alt"],
            self.refresh_servers
        )

        return ft.Container(
            content=ft.Column([
                header,
                self.refresh_btn,
                ft.Container(
                    content=self.servers_column,
                    border=ft.border.all(1, self.palette["line"]),
                    border_radius=12,
                    padding=10,
                    bgcolor=self.palette["panel"],
                    height=self.LIST_HEIGHT,
                    width=self.FIELD_WIDTH,
                    shadow=self.card_shadow
                ),
                pagination
            ], spacing=8),
            width=self.PANEL_WIDTH,
            padding=12,
            bgcolor=self.palette["panel"],
            border_radius=12,
            border=ft.border.all(1, self.palette["line"]),
            shadow=self.panel_shadow
        )

    def open_official_site(self, e):
        self.page.launch_url("https://github.com/jConjuring/VultrApiPanel")

    def set_status(self, message, color=None, update=True):
        self.status_text.value = message
        if color:
            self.status_text.color = color
        if update:
            self.page.update()

    def set_busy(self, busy, message=None, color=Colors.BLUE_700):
        if self.busy_indicator:
            self.busy_indicator.visible = busy
        for control in self.action_controls:
            if control:
                control.disabled = busy
        if message:
            self.set_status(message, color, update=False)
        self.page.update()

    def ensure_api(self):
        if not self.api:
            self.set_status("请先保存 API 密钥", Colors.RED_700)
            return False
        return True

    def save_api_key(self, e):
        api_key = self.api_key_input.value.strip()
        if api_key:
            self.config_manager.save_config(api_key)
            self.api = VultrAPI(api_key)
            self.set_status("API 密钥已保存，正在获取数据...", Colors.GREEN_700)
            self.query_all(None)
        else:
            self.set_status("请先保存 API 密钥", Colors.RED_700)

    def query_all(self, e):
        if not self.ensure_api():
            return

        self.set_busy(True, "正在获取区域、套餐和镜像...", Colors.BLUE_700)

        regions = self.api.get_regions()
        if regions:
            self.region_dropdown.options = [
                ft.dropdown.Option(key=r["id"], text=f"{r['city']} ({r['id']})")
                for r in regions if r.get("id")
            ]
            for option in self.region_dropdown.options:
                if "ewr" in option.key.lower():
                    self.region_dropdown.value = option.key
                    break
        else:
            self.region_dropdown.options = []
            self.region_dropdown.value = None

        plans = self.api.get_plans()
        if plans:
            self.plan_dropdown.options = [
                ft.dropdown.Option(
                    key=p["id"],
                    text=f"{p['id']} - ${p.get('monthly_cost', 0)}/mo"
                )
                for p in plans
            ]
            for option in self.plan_dropdown.options:
                if option.key == "vc2-1c-0.5gb":
                    self.plan_dropdown.value = option.key
                    break
        else:
            self.plan_dropdown.options = []
            self.plan_dropdown.value = None

        os_list = self.api.get_os_list()
        if os_list:
            sorted_os = self.sort_os_list(os_list)
            self.os_dropdown.options = [
                ft.dropdown.Option(key=str(os["id"]), text=os["name"])
                for os in sorted_os
            ]
            for option in self.os_dropdown.options:
                if "debian 12" in option.text.lower():
                    self.os_dropdown.value = option.key
                    break
        else:
            self.os_dropdown.options = []
            self.os_dropdown.value = None

        if regions and plans and os_list:
            self.set_status(
                f"获取完成！区域:{len(regions)} 套餐:{len(plans)} 镜像:{len(os_list)}",
                Colors.GREEN_700,
                update=False
            )
        else:
            self.set_status("获取失败，请检查 API 密钥或网络。", Colors.RED_700, update=False)

        self.refresh_servers(None, show_busy=False)
        self.set_busy(False)

    def sort_os_list(self, os_list):
        priority_order = {
            "debian": 1,
            "ubuntu": 2,
            "centos": 3,
            "windows": 4,
            "win": 4
        }

        def get_priority(os_item):
            name = os_item.get("name", "").lower()
            for keyword, priority in priority_order.items():
                if keyword in name:
                    return priority
            return 999

        return sorted(os_list, key=lambda item: (get_priority(item), item.get("name", "")))

    def buy_server(self, e):
        if not self.ensure_api():
            return

        region = self.region_dropdown.value
        plan = self.plan_dropdown.value
        os_id = self.os_dropdown.value

        if not all([region, plan, os_id]):
            self.set_status("请选择区域、套餐和系统", Colors.RED_700)
            return

        self.set_busy(True, "正在创建服务器...", Colors.BLUE_700)

        result = self.api.create_instance(region, plan, int(os_id))
        if result:
            self.set_status(
                f"服务器已创建，ID: {result.get('id', 'N/A')[:8]}...",
                Colors.GREEN_700,
                update=False
            )
            self.refresh_servers(None, show_busy=False)
        else:
            self.set_status("创建服务器失败", Colors.RED_700, update=False)

        self.set_busy(False)

    def refresh_servers(self, e, show_busy=True):
        if not self.ensure_api():
            return

        if show_busy:
            self.set_busy(True, "正在刷新服务器列表...", Colors.BLUE_700)
        else:
            self.set_status("正在刷新服务器列表...", Colors.BLUE_700)

        instances = self.api.get_instances()
        self.total_servers = []

        if instances:
            for inst in instances:
                detail = self.api.get_instance_detail(inst.get("id"))
                if detail:
                    inst.update(detail)
                self.total_servers.append(inst)

        self.current_page = 1
        self.update_server_display()

        if self.total_servers:
            self.server_count_text.value = f"共 {len(self.total_servers)} 台"
            self.set_status(f"共 {len(self.total_servers)} 台服务器", Colors.GREEN_700, update=False)
        else:
            self.server_count_text.value = "共 0 台"
            self.set_status("暂无服务器", Colors.GREEN_700, update=False)

        if show_busy:
            self.set_busy(False)
        else:
            self.page.update()

    def update_server_display(self):
        self.servers_column.controls.clear()

        if not self.total_servers:
            self.servers_column.controls.append(
                ft.Container(
                    content=ft.Text("暂无服务器", size=14, color=self.palette["muted"]),
                    alignment=ft.alignment.center,
                    height=self.LIST_HEIGHT - 50
                )
            )
            self.page_text.value = "第 1 页"
            self.prev_btn.disabled = True
            self.next_btn.disabled = True
            return

        total_pages = math.ceil(len(self.total_servers) / self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_servers = self.total_servers[start_idx:end_idx]

        for inst in current_servers:
            server_card = self.create_server_card(inst)
            self.servers_column.controls.append(server_card)

        self.page_text.value = f"第 {self.current_page}/{total_pages} 页"
        self.prev_btn.disabled = (self.current_page <= 1)
        self.next_btn.disabled = (self.current_page >= total_pages)

    def prev_page(self, e):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_server_display()
            self.page.update()

    def next_page(self, e):
        total_pages = math.ceil(len(self.total_servers) / self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_server_display()
            self.page.update()

    def create_server_card(self, instance):
        instance_id = instance.get("id", "N/A")
        ip = instance.get("main_ip", self.password_placeholder)
        password = instance.get("default_password", "") or self.password_placeholder
        label = instance.get("label") or instance.get("hostname") or "未命名"
        region = instance.get("region", "未知区域")
        plan = instance.get("plan", "未知套餐")
        os_name = instance.get("os", "未知系统")

        status = instance.get("status", "unknown")
        status_color = self.palette["success"] if status == "active" else self.palette["warning"]

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(label, size=12, weight=ft.FontWeight.BOLD, color=self.palette["text"]),
                        ft.Text(f"{region} | {plan}", size=10, color=self.palette["muted"]),
                        ft.Text(os_name, size=10, color=self.palette["muted"])
                    ], spacing=2),
                    ft.Container(
                        content=ft.Text(status, size=10, color=Colors.WHITE),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border_radius=4
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    ft.Text("IP：", size=11, width=35),
                    ft.Container(
                        content=ft.Text(ip, size=11, selectable=True),
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CONTENT_COPY,
                        icon_size=14,
                        tooltip="复制 IP",
                        icon_color=self.palette["accent"],
                        on_click=lambda e, text=ip: self.copy_to_clipboard(text)
                    )
                ]),

                ft.Row([
                    ft.Text("密码：", size=11, width=70),
                    ft.Container(
                        content=ft.Text(password[:15] + "..." if len(password) > 15 else password,
                                size=11, selectable=True),
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CONTENT_COPY,
                        icon_size=14,
                        tooltip="复制密码",
                        icon_color=self.palette["accent"],
                        on_click=lambda e, text=password: self.copy_to_clipboard(text),
                        disabled=(password == self.password_placeholder)
                    )
                ]),

                ft.Row([
                    ft.ElevatedButton(
                        text="重装",
                        on_click=lambda e, iid=instance_id: self.reinstall_server(iid),
                        width=165,
                        height=32,
                        bgcolor="#f59e0b",
                        color=Colors.WHITE
                    ),
                    ft.ElevatedButton(
                        text="删除",
                        on_click=lambda e, iid=instance_id: self.delete_server(iid),
                        bgcolor=self.palette["danger"],
                        color=Colors.WHITE,
                        width=165,
                        height=32
                    )
                ], spacing=5)
            ], spacing=6),
            border=ft.border.all(1, self.palette["line"]),
            border_radius=12,
            padding=10,
            bgcolor="#f8fafc",
            shadow=self.card_shadow
        )

    def copy_to_clipboard(self, text):
        if text == self.password_placeholder:
            self.set_status("密码暂未生成", Colors.ORANGE_700)
        else:
            self.page.set_clipboard(text)
            self.set_status(f"已复制: {text[:20]}...", Colors.GREEN_700)

    def reinstall_server(self, instance_id):
        if not self.ensure_api():
            return

        os_selector = ft.Dropdown(
            label="选择新系统",
            width=350,
            options=self.os_dropdown.options if self.os_dropdown.options else [],
            border_color=self.palette["line"],
            border_radius=8
        )

        for option in os_selector.options:
            if "debian 12" in option.text.lower():
                os_selector.value = option.key
                break

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def confirm_reinstall(e):
            if not os_selector.value:
                self.set_status("请选择系统", Colors.RED_700)
                return

            dialog.open = False
            self.page.update()

            self.set_busy(True, f"正在重装服务器 {instance_id[:8]}...", Colors.BLUE_700)

            success = self.api.reinstall_instance(instance_id, int(os_selector.value))
            if success:
                self.set_status(f"服务器 {instance_id[:8]} 已重装", Colors.GREEN_700, update=False)
                self.refresh_servers(None, show_busy=False)
            else:
                self.set_status("重装失败", Colors.RED_700, update=False)

            self.set_busy(False)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("重装系统", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"服务器 ID：{instance_id[:12]}...", size=12),
                    ft.Divider(),
                    os_selector,
                    ft.Container(height=5),
                    ft.Text("重装会清空所有数据。", size=11, color=Colors.ORANGE_700)
                ], spacing=10),
                width=400
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.ElevatedButton(
                    "确认重装",
                    bgcolor="#f59e0b",
                    color=Colors.WHITE,
                    on_click=confirm_reinstall
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def delete_server(self, instance_id):
        if not self.ensure_api():
            return

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def confirm_delete(e):
            dialog.open = False
            self.page.update()

            self.set_busy(True, f"正在删除服务器 {instance_id[:8]}...", Colors.BLUE_700)

            success = self.api.delete_instance(instance_id)
            if success:
                self.set_status(f"服务器 {instance_id[:8]} 已删除", Colors.GREEN_700, update=False)
                self.refresh_servers(None, show_busy=False)
            else:
                self.set_status("删除失败", Colors.RED_700, update=False)

            self.set_busy(False)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("确认删除", weight=ft.FontWeight.BOLD),
            content=ft.Text("此操作不可撤销，是否继续？", size=12),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.ElevatedButton(
                    "删除",
                    bgcolor=self.palette["danger"],
                    color=Colors.WHITE,
                    on_click=confirm_delete
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

def main(page: ft.Page):
    VultrManager(page)

if __name__ == "__main__":
    ft.app(target=main)
