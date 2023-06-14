/*
Copyright 2017 The Kubernetes Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Note: the example only works with the code within the same release/branch.

package watch

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"path/filepath"
	"strings"
	"time"

	v1 "github.com/fission/fission/pkg/apis/core/v1"
	"github.com/fission/fission/pkg/generated/clientset/versioned"
	"github.com/fission/fission/pkg/generated/informers/externalversions"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

type BuildResultPkg struct {
	Status    string `json:"status"`
	BuildInfo string `json:"buildInfo"`
	Name      string `json:"name"`
	Namespace string `json:"namespace"`
	UserId    string `json:"userId"`
}

type FeiShuInfo struct {
	Url string `json:"url"`
}

func StartWatch() {

	var kubeconfig *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to the kubeconfig file")
	}
	flag.Parse()

	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		panic(err)
	}
	fissionClientSet, err := versioned.NewForConfig(config)

	var a aaa
	factory := externalversions.NewSharedInformerFactory(fissionClientSet, 1*time.Second)
	_, err = factory.Core().V1().Packages().Informer().AddEventHandler(&a)
	//lister := factory.Core().V1().Packages().Lister()
	stopCh := make(chan struct{})
	factory.Start(stopCh)
	factory.WaitForCacheSync(stopCh)
	<-stopCh
}

type aaa struct {
}

func (a *aaa) OnAdd(obj interface{}) {
	fmt.Println("on add")
	objP1, ok := obj.(*v1.Package)
	if !ok {
		fmt.Println("发送新增pod信息失败")
		return
	}
	url := "http://0.0.0.0:8084/sendCreateStatus"

	fmt.Println("the add info:", objP1.Status.BuildStatus, objP1.ObjectMeta.Namespace, objP1.ObjectMeta.Name)
	fmt.Println("the add info 2:", objP1.Status.BuildStatus, objP1.Namespace, objP1.Name)
	if objP1.Status.BuildStatus == "failed" {
		url = "http://0.0.0.0:8084/sendUpdateStatus"
		SendUpdateInfo(objP1, url)
		return
	}
	SendAddInfo(objP1, url)
	//TODO implement me
}

func (a *aaa) OnUpdate(oldObj, newObj interface{}) {
	oldP1, ok := oldObj.(*v1.Package)
	if !ok {
		fmt.Println("转换失败")
		return
	}
	newP1, ok := newObj.(*v1.Package)
	if !ok {
		fmt.Println("转换失败")
		return
	}
	//TODO implement me
	if oldP1.UID != newP1.UID && oldP1.ResourceVersion != newP1.ResourceVersion {
		fmt.Println("资源有变更")
	} else {

		//fmt.Println("uid and reversion:", oldP1.UID, oldP1.ResourceVersion)
	}

	//fmt.Println("status:", newP1.TypeMeta.Kind, newP1.ObjectMeta)

	if newP1.Status.BuildStatus != oldP1.Status.BuildStatus {
		fmt.Println("the old and new:", newP1.Status.BuildStatus, oldP1.Status.BuildStatus)
		//fmt.Println("创建函数失败，失败日志为", oldP1.Status.BuildLog)
		url := "http://0.0.0.0:8084/sendUpdateStatus"
		SendUpdateInfo(oldP1, url)
	}
}

func (a *aaa) OnDelete(obj interface{}) {
	//TODO implement me
	fmt.Println("delete")
	objP1, ok := obj.(*v1.Package)
	if !ok {
		fmt.Println("发生删除pod信息失败")
		return
	}
	url := "http://0.0.0.0:8083/delete"
	SendUpdateInfo(objP1, url)
	//panic("implement me")
}

type LogData struct {
	BuildLogs string `json:"buildLogs"`
}

// SendUpdateInfo 应该是发送飞书消息通知函数创建状态的接口
func SendUpdateInfo(oldP1 *v1.Package, url string) {
	defer func() {
		if err := recover(); err != nil {
			fmt.Println("SendUpdateInfo err:", err)
		}
	}()
	jsonInfo := strings.Split(oldP1.Status.BuildLog, "Error building deployment package: Internal error - ")[1]
	tData := &LogData{}

	if err := json.Unmarshal([]byte(jsonInfo), tData); err != nil {
		fmt.Println("json data marshal failed", err.Error())
		return
	}
	fmt.Println("tData:", tData.BuildLogs)
	jsonInfo = strings.ReplaceAll(jsonInfo, "\\n", "\n")
	bytesData := []byte(tData.BuildLogs)
	encodeString := base64.StdEncoding.EncodeToString(bytesData)
	fmt.Println(encodeString)
	client := &http.Client{}
	da, err := json.Marshal(BuildResultPkg{
		Status:    string(oldP1.Status.BuildStatus),
		BuildInfo: encodeString,
		Namespace: oldP1.ObjectMeta.Namespace,
		Name:      oldP1.ObjectMeta.Name,
		UserId:    "helin1",
	})
	//fmt.Println("the data:", string(da))
	req, _ := http.NewRequest("POST", url, bytes.NewReader(da))
	req.Header.Add("Content-Type", "application/json")
	res, _ := client.Do(req)
	k, _ := json.Marshal(res)
	fmt.Println("the k is :", k)
	if res == nil {
		fmt.Println("body is nil")
		return
	}
	defer res.Body.Close()

	body, err := ioutil.ReadAll(res.Body)

	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println("the add info:", string(body))
}

// SendAddInfo 发送飞书消息通知函数创建状态的接口
func SendAddInfo(oldP1 *v1.Package, url string) {
	defer func() {
		if err := recover(); err != nil {
			fmt.Println("SendAddInfo err:", err)
		}
	}()
	client := &http.Client{}
	da, err := json.Marshal(BuildResultPkg{
		Status:    string(oldP1.Status.BuildStatus),
		BuildInfo: "function create succeeded",
		Namespace: oldP1.ObjectMeta.Namespace,
		Name:      oldP1.ObjectMeta.Name,
		UserId:    "helin1",
	})
	req, _ := http.NewRequest("POST", url, bytes.NewReader(da))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJBUFAiLCJpc3MiOiJTZXJ2aWNlIiwiZXhwIjoxNjc1OTA4NTkyLCJpYXQiOjE2NzU2NDkzOTIsInVzZXJuYW1lIjoiaGVsaW4xIn0.We2y16xXuDfyfD4cYqOgMirX78q-Cxo4DJym22aMeJ8")
	res, _ := client.Do(req)
	k, _ := json.Marshal(res)
	fmt.Println("the k is :", k)
	if res == nil {
		fmt.Println("body is nil")
		return
	}
	defer res.Body.Close()

	body, err := ioutil.ReadAll(res.Body)

	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println("the add info:", string(body))
}
