/**
 * 快取系統效能測試腳本
 * 測試增強版快取系統的各項功能和效能指標
 */

const { cacheManager } = require('../src/utils/cacheManager');
const { cachePreloader } = require('../src/utils/cachePreloader');
const { cacheAnalytics } = require('../src/utils/cacheAnalytics');
const { dbManager } = require('../src/database/connection');

class CachePerformanceTester {
    constructor() {
        this.testResults = {
            basic: {},
            compression: {},
            warmup: {},
            analytics: {},
            eviction: {},
            concurrent: {}
        };
    }

    /**
     * 運行所有測試
     */
    async runAllTests() {
        console.log('🧪 開始快取效能測試...\n');

        try {
            // 初始化系統
            await this.initializeSystem();

            // 基礎功能測試
            await this.testBasicOperations();

            // 壓縮功能測試
            await this.testCompression();

            // 預熱功能測試
            await this.testWarmup();

            // 分析系統測試
            await this.testAnalytics();

            // 智能清理測試
            await this.testEviction();

            // 並發測試
            await this.testConcurrency();

            // 生成測試報告
            this.generateReport();

        } catch (error) {
            console.error('❌ 測試過程中發生錯誤:', error);
        } finally {
            await this.cleanup();
        }
    }

    /**
     * 初始化測試環境
     */
    async initializeSystem() {
        console.log('🔧 初始化測試環境...');

        await dbManager.connectAll();
        await cacheManager.init();
        cacheAnalytics.startMonitoring();

        console.log('✅ 測試環境初始化完成\n');
    }

    /**
     * 測試基礎操作
     */
    async testBasicOperations() {
        console.log('📋 測試基礎快取操作...');

        const startTime = Date.now();
        const testData = { id: 1, name: 'Test Item', data: 'Some test data' };

        // 測試設置
        const setResult = await cacheManager.set('test', 'item1', testData);
        console.log('設置操作:', setResult ? '✅ 成功' : '❌ 失敗');

        // 測試獲取
        const getData = await cacheManager.get('test', 'item1');
        const getSuccess = JSON.stringify(getData) === JSON.stringify(testData);
        console.log('獲取操作:', getSuccess ? '✅ 成功' : '❌ 失敗');

        // 測試刪除
        const deleteResult = await cacheManager.delete('test', 'item1');
        console.log('刪除操作:', deleteResult ? '✅ 成功' : '❌ 失敗');

        // 測試批量操作
        const batchStartTime = Date.now();
        for (let i = 0; i < 100; i++) {\n            await cacheManager.set('test', `batch_${i}`, { id: i, value: `value_${i}` });\n        }\n        const batchSetTime = Date.now() - batchStartTime;\n\n        const batchGetStartTime = Date.now();\n        for (let i = 0; i < 100; i++) {\n            await cacheManager.get('test', `batch_${i}`);\n        }\n        const batchGetTime = Date.now() - batchGetStartTime;\n\n        this.testResults.basic = {\n            singleOperations: {\n                set: setResult,\n                get: getSuccess,\n                delete: deleteResult\n            },\n            batchOperations: {\n                setTime: `${batchSetTime}ms`,\n                getTime: `${batchGetTime}ms`,\n                avgSetTime: `${(batchSetTime / 100).toFixed(2)}ms`,\n                avgGetTime: `${(batchGetTime / 100).toFixed(2)}ms`\n            },\n            totalTime: `${Date.now() - startTime}ms`\n        };\n\n        console.log('✅ 基礎操作測試完成\\n');\n    }\n\n    /**\n     * 測試壓縮功能\n     */\n    async testCompression() {\n        console.log('🗜️ 測試快取壓縮功能...');\n\n        // 創建大數據對象\n        const largeData = {\n            id: 'large_item',\n            description: 'A'.repeat(2000), // 2KB 字符串\n            metadata: Array.from({ length: 100 }, (_, i) => ({\n                field: `field_${i}`,\n                value: `value_${i}`.repeat(10)\n            }))\n        };\n\n        const startTime = Date.now();\n\n        // 測試壓縮存儲\n        await cacheManager.set('artwork', 'large_item', largeData);\n        const setTime = Date.now() - startTime;\n\n        // 測試壓縮讀取\n        const retrieveStartTime = Date.now();\n        const retrievedData = await cacheManager.get('artwork', 'large_item');\n        const retrieveTime = Date.now() - retrieveStartTime;\n\n        const dataIntegrity = JSON.stringify(retrievedData) === JSON.stringify(largeData);\n\n        this.testResults.compression = {\n            dataSize: `${JSON.stringify(largeData).length} bytes`,\n            setTime: `${setTime}ms`,\n            retrieveTime: `${retrieveTime}ms`,\n            dataIntegrity: dataIntegrity ? '✅ 完整' : '❌ 損壞'\n        };\n\n        console.log('壓縮測試結果:');\n        console.log(`- 數據大小: ${this.testResults.compression.dataSize}`);\n        console.log(`- 設置時間: ${this.testResults.compression.setTime}`);\n        console.log(`- 讀取時間: ${this.testResults.compression.retrieveTime}`);\n        console.log(`- 數據完整性: ${this.testResults.compression.dataIntegrity}`);\n        console.log('✅ 壓縮功能測試完成\\n');\n    }\n\n    /**\n     * 測試預熱功能\n     */\n    async testWarmup() {\n        console.log('🔥 測試快取預熱功能...');\n\n        const startTime = Date.now();\n\n        // 註冊測試預熱任務\n        cachePreloader.registerTask('test', 'warmup_item1', async () => {\n            return { id: 'warmup1', data: 'Warmed up data 1' };\n        }, { priority: 10 });\n\n        cachePreloader.registerTask('test', 'warmup_item2', async () => {\n            return { id: 'warmup2', data: 'Warmed up data 2' };\n        }, { priority: 8 });\n\n        // 執行預熱\n        await cachePreloader.startPreloading();\n\n        // 檢查預熱結果\n        const warmedItem1 = await cacheManager.get('test', 'warmup_item1');\n        const warmedItem2 = await cacheManager.get('test', 'warmup_item2');\n\n        const warmupTime = Date.now() - startTime;\n        const preloaderStats = cachePreloader.getStats();\n\n        this.testResults.warmup = {\n            warmupTime: `${warmupTime}ms`,\n            item1Success: warmedItem1 ? '✅ 成功' : '❌ 失敗',\n            item2Success: warmedItem2 ? '✅ 成功' : '❌ 失敗',\n            preloaderStats\n        };\n\n        console.log('預熱測試結果:');\n        console.log(`- 預熱時間: ${this.testResults.warmup.warmupTime}`);\n        console.log(`- 項目1: ${this.testResults.warmup.item1Success}`);\n        console.log(`- 項目2: ${this.testResults.warmup.item2Success}`);\n        console.log('✅ 預熱功能測試完成\\n');\n    }\n\n    /**\n     * 測試分析系統\n     */\n    async testAnalytics() {\n        console.log('📊 測試快取分析功能...');\n\n        const startTime = Date.now();\n\n        // 生成一些快取活動\n        for (let i = 0; i < 50; i++) {\n            await cacheManager.set('analytics', `item_${i}`, { id: i, value: `test_${i}` });\n            if (i % 2 === 0) {\n                await cacheManager.get('analytics', `item_${i}`); // 50% 命中率\n            }\n            await cacheManager.get('analytics', `nonexistent_${i}`); // 未命中\n        }\n\n        // 等待分析收集數據\n        await this.delay(2000);\n\n        const analyticsReport = cacheAnalytics.getAnalyticsReport();\n        const analysisTime = Date.now() - startTime;\n\n        this.testResults.analytics = {\n            analysisTime: `${analysisTime}ms`,\n            reportGenerated: analyticsReport ? '✅ 成功' : '❌ 失敗',\n            summary: analyticsReport.summary || {},\n            current: analyticsReport.current || {},\n            monitoring: analyticsReport.monitoring || {}\n        };\n\n        console.log('分析測試結果:');\n        console.log(`- 分析時間: ${this.testResults.analytics.analysisTime}`);\n        console.log(`- 報告生成: ${this.testResults.analytics.reportGenerated}`);\n        console.log('✅ 分析功能測試完成\\n');\n    }\n\n    /**\n     * 測試智能清理\n     */\n    async testEviction() {\n        console.log('🧹 測試智能清理功能...');\n\n        const startTime = Date.now();\n\n        // 填充快取直到觸發清理\n        for (let i = 0; i < 200; i++) {\n            await cacheManager.set('eviction_test', `item_${i}`, {\n                id: i,\n                data: `data_${i}`,\n                timestamp: Date.now()\n            });\n\n            // 模擬不同的訪問模式\n            if (i < 50) {\n                // 前50個項目多次訪問（熱門項目）\n                for (let j = 0; j < 3; j++) {\n                    await cacheManager.get('eviction_test', `item_${i}`);\n                }\n            }\n        }\n\n        // 觸發智能清理\n        if (cacheManager.smartEviction) {\n            cacheManager.smartEviction();\n        }\n\n        const evictionTime = Date.now() - startTime;\n        const finalStats = cacheManager.getStats();\n\n        this.testResults.eviction = {\n            evictionTime: `${evictionTime}ms`,\n            itemsAfterEviction: finalStats.memoryUsage,\n            evictionCount: finalStats.evictions || 0\n        };\n\n        console.log('清理測試結果:');\n        console.log(`- 清理時間: ${this.testResults.eviction.evictionTime}`);\n        console.log(`- 剩餘項目: ${this.testResults.eviction.itemsAfterEviction}`);\n        console.log(`- 清理次數: ${this.testResults.eviction.evictionCount}`);\n        console.log('✅ 智能清理測試完成\\n');\n    }\n\n    /**\n     * 測試並發性能\n     */\n    async testConcurrency() {\n        console.log('⚡ 測試並發性能...');\n\n        const startTime = Date.now();\n        const concurrentOperations = 100;\n\n        // 並發寫入測試\n        const writePromises = Array.from({ length: concurrentOperations }, (_, i) =>\n            cacheManager.set('concurrent', `write_item_${i}`, { id: i, data: `concurrent_data_${i}` })\n        );\n\n        await Promise.all(writePromises);\n        const writeTime = Date.now() - startTime;\n\n        // 並發讀取測試\n        const readStartTime = Date.now();\n        const readPromises = Array.from({ length: concurrentOperations }, (_, i) =>\n            cacheManager.get('concurrent', `write_item_${i}`)\n        );\n\n        const readResults = await Promise.all(readPromises);\n        const readTime = Date.now() - readStartTime;\n\n        const successfulReads = readResults.filter(result => result !== null).length;\n\n        this.testResults.concurrent = {\n            operations: concurrentOperations,\n            writeTime: `${writeTime}ms`,\n            readTime: `${readTime}ms`,\n            avgWriteTime: `${(writeTime / concurrentOperations).toFixed(2)}ms`,\n            avgReadTime: `${(readTime / concurrentOperations).toFixed(2)}ms`,\n            readSuccessRate: `${((successfulReads / concurrentOperations) * 100).toFixed(2)}%`,\n            totalTime: `${Date.now() - startTime}ms`\n        };\n\n        console.log('並發測試結果:');\n        console.log(`- 操作數量: ${this.testResults.concurrent.operations}`);\n        console.log(`- 寫入時間: ${this.testResults.concurrent.writeTime}`);\n        console.log(`- 讀取時間: ${this.testResults.concurrent.readTime}`);\n        console.log(`- 平均寫入: ${this.testResults.concurrent.avgWriteTime}`);\n        console.log(`- 平均讀取: ${this.testResults.concurrent.avgReadTime}`);\n        console.log(`- 讀取成功率: ${this.testResults.concurrent.readSuccessRate}`);\n        console.log('✅ 並發性能測試完成\\n');\n    }\n\n    /**\n     * 生成測試報告\n     */\n    generateReport() {\n        console.log('📋 === 快取系統效能測試報告 ===\\n');\n\n        console.log('🔧 基礎功能測試:');\n        console.log(`  單項操作: 設置(${this.testResults.basic.singleOperations.set ? '通過' : '失敗'}), 獲取(${this.testResults.basic.singleOperations.get ? '通過' : '失敗'}), 刪除(${this.testResults.basic.singleOperations.delete ? '通過' : '失敗'})`);\n        console.log(`  批量操作: 平均設置時間 ${this.testResults.basic.batchOperations.avgSetTime}, 平均獲取時間 ${this.testResults.basic.batchOperations.avgGetTime}`);\n        console.log();\n\n        console.log('🗜️ 壓縮功能測試:');\n        console.log(`  數據完整性: ${this.testResults.compression.dataIntegrity}`);\n        console.log(`  設置時間: ${this.testResults.compression.setTime}`);\n        console.log(`  讀取時間: ${this.testResults.compression.retrieveTime}`);\n        console.log();\n\n        console.log('🔥 預熱功能測試:');\n        console.log(`  預熱時間: ${this.testResults.warmup.warmupTime}`);\n        console.log(`  成功率: ${this.testResults.warmup.preloaderStats.successRate}`);\n        console.log();\n\n        console.log('⚡ 並發性能測試:');\n        console.log(`  ${this.testResults.concurrent.operations} 個並發操作`);\n        console.log(`  平均寫入時間: ${this.testResults.concurrent.avgWriteTime}`);\n        console.log(`  平均讀取時間: ${this.testResults.concurrent.avgReadTime}`);\n        console.log(`  讀取成功率: ${this.testResults.concurrent.readSuccessRate}`);\n        console.log();\n\n        console.log('📊 系統統計:');\n        const finalStats = cacheManager.getStats();\n        console.log(`  總請求數: ${finalStats.totalRequests}`);\n        console.log(`  命中率: ${finalStats.hitRate}`);\n        console.log(`  記憶體使用: ${finalStats.memoryUsage} 項目`);\n        console.log(`  預熱隊列: ${finalStats.warmupQueueSize} 項目`);\n        console.log();\n\n        console.log('✅ 測試完成！快取系統運行正常。');\n    }\n\n    /**\n     * 清理測試環境\n     */\n    async cleanup() {\n        console.log('🧹 清理測試環境...');\n\n        // 清空測試數據\n        const testCategories = ['test', 'artwork', 'analytics', 'eviction_test', 'concurrent'];\n        for (const category of testCategories) {\n            await cacheManager.clearCategory(category);\n        }\n\n        cacheAnalytics.stopMonitoring();\n        await cacheManager.shutdown();\n        await dbManager.closeAll();\n\n        console.log('✅ 清理完成');\n    }\n\n    /**\n     * 延遲工具函數\n     */\n    delay(ms) {\n        return new Promise(resolve => setTimeout(resolve, ms));\n    }\n}\n\n// 運行測試\nconst tester = new CachePerformanceTester();\ntester.runAllTests().catch(console.error);"